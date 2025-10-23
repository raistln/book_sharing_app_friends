"""
Servicio para gestión de grupos de usuarios.
"""
from typing import List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
import uuid

from app.models.group import Group, GroupMember, GroupRole
from app.models.invitation import Invitation
from app.models.user import User

from app.schemas.group import GroupCreate, GroupUpdate, GroupMemberCreate, GroupMemberUpdate
from app.schemas.invitation import InvitationCreate
from app.utils.security import hash_password


logger = logging.getLogger(__name__)


class GroupService:
    def __init__(self, db: Session):
        self.db = db

    def create_group(self, group_data: GroupCreate, creator_id: uuid.UUID) -> Group:
        """Crear un nuevo grupo."""
        logger.info("create_group name=%s creator_id=%s", group_data.name, str(creator_id))
        # Crear el grupo
        group = Group(
            name=group_data.name,
            description=group_data.description,
            created_by=creator_id
        )
        self.db.add(group)
        self.db.flush()  # Para obtener el ID del grupo

        # Añadir al creador como admin
        creator_membership = GroupMember(
            group_id=group.id,
            user_id=creator_id,
            role=GroupRole.ADMIN
        )
        self.db.add(creator_membership)
        self.db.commit()
        self.db.refresh(group)
        logger.info("create_group success group_id=%s", str(group.id))
        
        return group

    def get_group(self, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Group]:
        """Obtener un grupo (solo si el usuario es miembro)."""
        return self.db.query(Group).join(GroupMember).filter(
            and_(
                Group.id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()

    def get_user_groups(self, user_id: uuid.UUID) -> List[Group]:
        """Obtener todos los grupos del usuario."""
        return self.db.query(Group).join(GroupMember).filter(
            GroupMember.user_id == user_id
        ).all()

    def update_group(self, group_id: uuid.UUID, user_id: uuid.UUID, group_data: GroupUpdate) -> Optional[Group]:
        """Actualizar un grupo (solo admins)."""
        logger.info("update_group group_id=%s user_id=%s", str(group_id), str(user_id))
        group = self.get_group(group_id, user_id)
        if not group or not self.is_group_admin(group_id, user_id):
            return None

        if group_data.name is not None:
            group.name = group_data.name
        if group_data.description is not None:
            group.description = group_data.description

        group.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(group)
        logger.info("update_group success group_id=%s", str(group.id))
        return group

    def delete_group(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Eliminar un grupo (solo el creador)."""
        logger.info("delete_group group_id=%s user_id=%s", str(group_id), str(user_id))
        group = self.db.query(Group).filter(
            and_(
                Group.id == group_id,
                Group.created_by == user_id
            )
        ).first()

        if not group:
            return False

        self.db.delete(group)
        self.db.commit()
        logger.info("delete_group success group_id=%s", str(group_id))
        return True

    def add_member(self, group_id: uuid.UUID, user_id: uuid.UUID, member_data: GroupMemberCreate) -> Optional[GroupMember]:
        """Añadir un miembro al grupo (solo admins)."""
        logger.info("add_member group_id=%s actor_id=%s member_id=%s role=%s", str(group_id), str(user_id), str(member_data.user_id), member_data.role)
        if not self.is_group_admin(group_id, user_id):
            return None

        # Verificar que el usuario no sea ya miembro
        existing_member = self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_data.user_id
            )
        ).first()

        if existing_member:
            return None

        member = GroupMember(
            group_id=group_id,
            user_id=member_data.user_id,
            role=member_data.role,
            invited_by=user_id
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        logger.info("add_member success group_id=%s member_id=%s", str(group_id), str(member.user_id))
        return member

    def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID, member_id: uuid.UUID) -> bool:
        """Remover un miembro del grupo (solo admins)."""
        logger.info("remove_member group_id=%s actor_id=%s member_id=%s", str(group_id), str(user_id), str(member_id))
        if not self.is_group_admin(group_id, user_id):
            return False

        member = self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_id
            )
        ).first()

        if not member:
            return False

        self.db.delete(member)
        self.db.commit()
        logger.info("remove_member success group_id=%s member_id=%s", str(group_id), str(member_id))
        return True

    def leave_group(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Permite a un miembro salir voluntariamente de un grupo."""
        logger.info("leave_group group_id=%s user_id=%s", str(group_id), str(user_id))
        
        # Verificar que el grupo existe
        group = self.db.query(Group).filter(Group.id == group_id).first()
        if not group:
            logger.warning("leave_group failed: group not found")
            return False
        
        # No permitir que el creador salga del grupo
        if group.created_by == user_id:
            logger.warning("leave_group failed: creator cannot leave")
            return False
        
        # Obtener el miembro
        member = self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if not member:
            logger.warning("leave_group failed: user is not a member")
            return False
        
        # Si es admin, verificar que no sea el último admin
        if member.role == GroupRole.ADMIN:
            admin_count = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.role == GroupRole.ADMIN
                )
            ).count()
            
            if admin_count <= 1:
                logger.warning("leave_group failed: last admin cannot leave")
                return False
        
        # Eliminar el miembro
        self.db.delete(member)
        self.db.commit()
        logger.info("leave_group success group_id=%s user_id=%s", str(group_id), str(user_id))
        return True

    def update_member_role(self, group_id: uuid.UUID, user_id: uuid.UUID, member_id: uuid.UUID, role_data: GroupMemberUpdate) -> Optional[GroupMember]:
        """Actualizar el rol de un miembro (solo admins)."""
        logger.info("update_member_role group_id=%s actor_id=%s member_id=%s new_role=%s", str(group_id), str(user_id), str(member_id), role_data.role)
        if not self.is_group_admin(group_id, user_id):
            return None

        member = self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_id
            )
        ).first()

        if not member:
            return None

        member.role = role_data.role
        self.db.commit()
        self.db.refresh(member)
        logger.info("update_member_role success group_id=%s member_id=%s role=%s", str(group_id), str(member.user_id), member.role)
        return member

    def is_group_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Verificar si un usuario es miembro de un grupo."""
        return self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first() is not None

    def is_group_admin(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Verificar si un usuario es admin de un grupo."""
        member = self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.role == GroupRole.ADMIN
            )
        ).first()
        return member is not None

    def get_group_members(self, group_id: uuid.UUID, user_id: uuid.UUID) -> List[GroupMember]:
        """Obtener miembros de un grupo (solo si el usuario es miembro)."""
        if not self.is_group_member(group_id, user_id):
            return []

        return self.db.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).all()

    def create_invitation(self, group_id: uuid.UUID, user_id: uuid.UUID, invitation_data: InvitationCreate) -> Optional[Invitation]:
        """Crear una invitación a un grupo (solo admins)."""
        logger.info("create_invitation group_id=%s actor_id=%s email=%s username=%s", 
                   str(group_id), str(user_id), invitation_data.email, invitation_data.username)
        if not self.is_group_admin(group_id, user_id):
            return None

        # Determinar el email a usar
        email_to_use = invitation_data.email or ""
        
        # Si se proporciona username, buscar el email del usuario
        if invitation_data.username and not invitation_data.email:
            user = self.db.query(User).filter(User.username == invitation_data.username).first()
            if user:
                email_to_use = user.email
            else:
                logger.warning("create_invitation username not found: %s", invitation_data.username)
                return None

        # Si se proporciona email, verificar que no exista una invitación pendiente
        if email_to_use:
            existing_invitation = self.db.query(Invitation).filter(
                and_(
                    Invitation.group_id == group_id,
                    Invitation.email == email_to_use,
                    Invitation.is_accepted.is_(None)
                )
            ).first()

            if existing_invitation:
                return None

        # Crear la invitación sin expiración (expires_at en el futuro lejano)
        import uuid as _uuid
        invitation = Invitation(
            group_id=group_id,
            email=email_to_use,
            message=invitation_data.message,
            invited_by=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),  # 1 año de validez
            code=_uuid.uuid4().hex
        )
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        logger.info("create_invitation success invitation_id=%s email=%s code=%s", str(invitation.id), invitation.email, invitation.code)
        
        return invitation

    def get_user_invitations(self, email: str) -> List[Invitation]:
        """Obtener invitaciones pendientes de un usuario por email."""
        return self.db.query(Invitation).filter(
            and_(
                Invitation.email == email,
                Invitation.is_accepted.is_(None),
                Invitation.expires_at > datetime.now(timezone.utc)
            )
        ).all()

    def get_group_invitations(self, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[List[Invitation]]:
        """Obtener todas las invitaciones de un grupo (solo admins)."""
        logger.info("get_group_invitations group_id=%s actor_id=%s", str(group_id), str(user_id))

        if not self.is_group_admin(group_id, user_id):
            logger.warning("get_group_invitations denied: user is not admin")
            return None

        invitations = self.db.query(Invitation).filter(
            Invitation.group_id == group_id
        ).order_by(Invitation.created_at.desc()).all()

        logger.info("get_group_invitations success group_id=%s count=%s", str(group_id), len(invitations))
        return invitations

    def cancel_invitation(self, group_id: uuid.UUID, invitation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Cancelar una invitación (solo admins)."""
        logger.info("cancel_invitation group_id=%s invitation_id=%s actor_id=%s", str(group_id), str(invitation_id), str(user_id))
        if not self.is_group_admin(group_id, user_id):
            return False

        invitation = self.db.query(Invitation).filter(
            and_(
                Invitation.id == invitation_id,
                Invitation.group_id == group_id
            )
        ).first()

        if not invitation:
            return False

        self.db.delete(invitation)
        self.db.commit()
        logger.info("cancel_invitation success invitation_id=%s", str(invitation_id))
        return True

    def respond_to_invitation(self, invitation_id: uuid.UUID, email: str, accept: bool) -> Optional[GroupMember]:
        """Responder a una invitación."""
        logger.info("respond_to_invitation invitation_id=%s email=%s accept=%s", str(invitation_id), email, accept)
        invitation = self.db.query(Invitation).filter(
            and_(
                Invitation.id == invitation_id,
                Invitation.email == email,
                Invitation.is_accepted.is_(None)
            )
        ).first()

        if not invitation:
            return None

        invitation.is_accepted = accept
        invitation.responded_at = datetime.now(timezone.utc)

        if accept:
            # Buscar el usuario por email
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return None

            # Añadir como miembro del grupo
            member = GroupMember(
                group_id=invitation.group_id,
                user_id=user.id,
                role=GroupRole.MEMBER,
                invited_by=invitation.invited_by
            )
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            logger.info("respond_to_invitation accepted invitation_id=%s member_id=%s", str(invitation_id), str(member.user_id))
            return member
        else:
            self.db.commit()
            logger.info("respond_to_invitation rejected invitation_id=%s", str(invitation_id))
            return None
