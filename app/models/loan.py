"""
Modelo de Préstamo (Loan)
"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class LoanStatus(enum.Enum):
    requested = "requested"
    approved = "approved"
    active = "active"
    returned = "returned"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True)

    status = Column(Enum(LoanStatus, name="loan_status"), nullable=False, server_default=LoanStatus.requested.name)

    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones ORM
    book = relationship("Book", lazy="joined")
    borrower = relationship("User", foreign_keys=[borrower_id], lazy="joined")
    lender = relationship("User", foreign_keys=[lender_id], lazy="joined")
    group = relationship("Group", back_populates="loans")

    def __repr__(self):
        return f"<Loan(id={self.id}, book_id={self.book_id}, status={self.status})>"


