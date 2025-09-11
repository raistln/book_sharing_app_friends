"""
Endpoints para gestión de grupos de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.group_service import GroupService
from app.models.user import User
from app.schemas.group import (
    Group, GroupCreate, GroupUpdate, GroupSummary,
    GroupMember, GroupMemberCreate, GroupMemberUpdate, GroupMemberWithUser
)
from app.schemas.invitation import Invitation, InvitationCreate, InvitationResponse

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo grupo."""
    group_service = GroupService(db)
    group = group_service.create_group(group_data, current_user.id)
    return group


@router.get("/", response_model=List[GroupSummary])
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los grupos del usuario."""
    group_service = GroupService(db)
    groups = group_service.get_user_groups(current_user.id)
    
    # Convertir a GroupSummary con información adicional
    group_summaries = []
    for group in groups:
        member_count = len(group.members)
        admin_count = sum(1 for member in group.members if member.role.value == "admin")
        is_admin = any(member.user_id == current_user.id and member.role.value == "admin" for member in group.members)
        
        group_summaries.append(GroupSummary(
            id=group.id,
            name=group.name,
            description=group.description,
            member_count=member_count,
            created_at=group.created_at,
            is_admin=is_admin
        ))
    
    return group_summaries


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un grupo específico."""
    group_service = GroupService(db)
    group = group_service.get_group(group_id, current_user.id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return group


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un grupo (solo admins)."""
    group_service = GroupService(db)
    group = group_service.update_group(group_id, current_user.id, group_data)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos de administrador"
        )
    
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un grupo (solo el creador)."""
    group_service = GroupService(db)
    success = group_service.delete_group(group_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no eres el creador"
        )


@router.get("/{group_id}/members", response_model=List[GroupMemberWithUser])
async def get_group_members(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener miembros de un grupo."""
    group_service = GroupService(db)
    members = group_service.get_group_members(group_id, current_user.id)
    
    if members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return members


@router.post("/{group_id}/members", response_model=GroupMember, status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: UUID,
    member_data: GroupMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añadir un miembro al grupo (solo admins)."""
    group_service = GroupService(db)
    member = group_service.add_member(group_id, current_user.id, member_data)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo añadir el miembro. Verifica que seas admin y el usuario no sea ya miembro"
        )
    
    return member


@router.put("/{group_id}/members/{member_id}", response_model=GroupMember)
async def update_member_role(
    group_id: UUID,
    member_id: UUID,
    role_data: GroupMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar el rol de un miembro (solo admins)."""
    group_service = GroupService(db)
    member = group_service.update_member_role(group_id, current_user.id, member_id, role_data)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado o no tienes permisos de administrador"
        )
    
    return member


@router.delete("/{group_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_member(
    group_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remover un miembro del grupo (solo admins)."""
    group_service = GroupService(db)
    success = group_service.remove_member(group_id, current_user.id, member_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado o no tienes permisos de administrador"
        )


@router.post("/{group_id}/invitations", response_model=Invitation, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    group_id: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una invitación a un grupo (solo admins)."""
    group_service = GroupService(db)
    invitation = group_service.create_invitation(group_id, current_user.id, invitation_data)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la invitación. Verifica que seas admin y no exista una invitación pendiente"
        )
    
    return invitation


@router.get("/{group_id}/invitations", response_model=List[Invitation])
async def get_group_invitations(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener invitaciones de un grupo (solo admins)."""
    group_service = GroupService(db)
    invitations = group_service.get_group_invitations(group_id, current_user.id)
    
    if invitations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos de administrador"
        )
    
    return invitations


@router.get("/invitations/pending", response_model=List[Invitation])
async def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener invitaciones pendientes del usuario."""
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener un email para recibir invitaciones"
        )
    
    group_service = GroupService(db)
    invitations = group_service.get_user_invitations(current_user.email)
    return invitations


@router.post("/invitations/{invitation_id}/respond", response_model=GroupMember)
async def respond_to_invitation(
    invitation_id: UUID,
    response_data: InvitationResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Responder a una invitación."""
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener un email para responder invitaciones"
        )
    
    group_service = GroupService(db)
    member = group_service.respond_to_invitation(
        invitation_id, 
        current_user.email, 
        response_data.accept
    )
    
    if not member and response_data.accept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo aceptar la invitación. Verifica que la invitación sea válida"
        )
    
    return member
