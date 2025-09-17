"""
Schemas Pydantic para grupos de usuarios.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.models.group import GroupRole


class GroupBase(BaseModel):
    """Schema base para grupos."""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del grupo")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del grupo")


class GroupCreate(GroupBase):
    """Schema para crear un grupo."""
    pass


class GroupUpdate(BaseModel):
    """Schema para actualizar un grupo."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class GroupMemberBase(BaseModel):
    """Schema base para miembros de grupo."""
    role: GroupRole = Field(default=GroupRole.MEMBER, description="Rol del usuario en el grupo")


class GroupMemberCreate(GroupMemberBase):
    """Schema para añadir un miembro a un grupo."""
    user_id: UUID = Field(..., description="ID del usuario a añadir")


class GroupMemberUpdate(BaseModel):
    """Schema para actualizar el rol de un miembro."""
    role: GroupRole = Field(..., description="Nuevo rol del usuario")


class GroupMember(GroupMemberBase):
    """Schema para representar un miembro de grupo."""
    id: UUID
    group_id: UUID
    user_id: UUID
    joined_at: datetime
    invited_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class GroupMemberWithUser(GroupMember):
    """Schema para miembro con información del usuario."""
    user: "UserBasic"

    model_config = ConfigDict(from_attributes=True)


class Group(GroupBase):
    """Schema para representar un grupo."""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    members: List[GroupMemberWithUser] = []

    model_config = ConfigDict(from_attributes=True)


class GroupWithMembers(Group):
    """Schema para grupo con información detallada de miembros."""
    member_count: int = Field(..., description="Número total de miembros")
    admin_count: int = Field(..., description="Número de administradores")


class GroupSummary(BaseModel):
    """Schema resumido para listar grupos."""
    id: UUID
    name: str
    description: Optional[str] = None
    member_count: int
    created_at: datetime
    is_admin: bool = Field(..., description="Si el usuario actual es admin del grupo")

    model_config = ConfigDict(from_attributes=True)


# Importación circular resuelta
from app.schemas.user import UserBasic
GroupMemberWithUser.model_rebuild()
