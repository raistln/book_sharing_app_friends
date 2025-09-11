"""
Modelo SQLAlchemy para grupos de usuarios.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class GroupRole(str, enum.Enum):
    """Roles de usuario en un grupo."""
    ADMIN = "admin"
    MEMBER = "member"


class Group(Base):
    """Modelo para grupos de usuarios."""
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    creator = relationship("User", back_populates="created_groups", foreign_keys=[created_by])
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="group")
    invitations = relationship("Invitation", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"


class GroupMember(Base):
    """Modelo para miembros de grupos (relación many-to-many)."""
    __tablename__ = "group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(GroupRole), default=GroupRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relaciones
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships", foreign_keys=[user_id])
    inviter = relationship("User", back_populates="sent_invitations", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<GroupMember(group_id={self.group_id}, user_id={self.user_id}, role='{self.role}')>"
