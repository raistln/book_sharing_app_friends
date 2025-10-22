"""
Schemas Pydantic para invitaciones a grupos.
"""
from pydantic import BaseModel, Field, EmailStr
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class InvitationBase(BaseModel):
    """Schema base para invitaciones."""
    email: Optional[EmailStr] = Field(None, description="Email del usuario a invitar (opcional)")
    username: Optional[str] = Field(None, description="Username del usuario a invitar (opcional)")
    message: Optional[str] = Field(None, max_length=500, description="Mensaje personal opcional")


class InvitationCreate(InvitationBase):
    """Schema para crear una invitación."""
    pass


class InvitationResponse(BaseModel):
    """Schema para responder a una invitación."""
    accept: bool = Field(..., description="True para aceptar, False para rechazar")


class Invitation(InvitationBase):
    """Schema para representar una invitación."""
    id: UUID
    group_id: UUID
    invited_by: UUID
    created_at: datetime
    expires_at: datetime
    is_accepted: Optional[bool] = None
    responded_at: Optional[datetime] = None
    code: str

    model_config = ConfigDict(from_attributes=True)


class InvitationWithGroup(Invitation):
    """Schema para invitación con información del grupo."""
    group: "GroupSummary"

    model_config = ConfigDict(from_attributes=True)


class InvitationSummary(BaseModel):
    """Schema resumido para listar invitaciones."""
    id: UUID
    group_name: str
    invited_by: str
    created_at: datetime
    expires_at: datetime
    is_accepted: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


# Importación circular resuelta
from app.schemas.group import GroupSummary
InvitationWithGroup.model_rebuild()
