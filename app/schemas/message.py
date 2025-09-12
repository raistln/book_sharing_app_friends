"""
Schemas Pydantic para mensajes de chat.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    loan_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)


class Message(BaseModel):
    id: UUID
    loan_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


