"""
Modelo SQLAlchemy para invitaciones a grupos.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Invitation(Base):
    """Modelo para invitaciones a grupos."""
    __tablename__ = "invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=True)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_accepted = Column(Boolean, nullable=True, default=None)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    # Código único para aceptar invitación vía enlace
    code = Column(String(64), unique=True, index=True, nullable=False, default=lambda: uuid.uuid4().hex)

    # Relaciones
    group = relationship("Group", back_populates="invitations")
    inviter = relationship("User", back_populates="sent_group_invitations")

    def __repr__(self):
        return f"<Invitation(id={self.id}, group_id={self.group_id}, email='{self.email}')>"

    @property
    def is_expired(self) -> bool:
        """Verifica si la invitación ha expirado."""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at

    @property
    def is_pending(self) -> bool:
        """Verifica si la invitación está pendiente."""
        return self.is_accepted is None and not self.is_expired
