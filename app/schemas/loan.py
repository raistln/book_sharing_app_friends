"""
Schemas Pydantic para Préstamos (Loan)
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class LoanBase(BaseModel):
    book_id: UUID
    borrower_id: UUID
    lender_id: UUID
    group_id: Optional[UUID] = None
    status: Optional[str] = Field("requested", pattern="^(requested|approved|active|returned)$")
    due_date: Optional[datetime] = None


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(requested|approved|active|returned)$")
    approved_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    returned_at: Optional[datetime] = None


class LoanInDB(LoanBase):
    id: UUID
    requested_at: datetime
    approved_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class Loan(LoanInDB):
    pass


