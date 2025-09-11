"""
Modelo de Usuario
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base
# Importar modelos relacionados para registrar clases en el mapper y evitar errores de resolución perezosa
from app.models.group import Group, GroupMember  # noqa: F401
from app.models.invitation import Invitation  # noqa: F401


class User(Base):
    __tablename__ = "users"
    
    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Campos de estado
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Campos de auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Campos opcionales
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Relaciones
    created_groups = relationship("Group", back_populates="creator")
    group_memberships = relationship("GroupMember", back_populates="user", foreign_keys="GroupMember.user_id")
    sent_invitations = relationship("GroupMember", back_populates="inviter", foreign_keys="GroupMember.invited_by")
    sent_group_invitations = relationship("Invitation", back_populates="inviter")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
