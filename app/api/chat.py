"""
Endpoints de chat (mensajes) por préstamo.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate, Message as MessageSchema
from app.models.user import User


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
def send_message(payload: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = MessageService(db)
    msg = svc.send(payload.loan_id, current_user.id, payload.content)
    if not msg:
        raise HTTPException(status_code=403, detail="No tienes acceso a este préstamo")
    return msg


@router.get("/loan/{loan_id}", response_model=list[MessageSchema])
def get_messages(loan_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = MessageService(db)
    items = svc.list_for_loan(loan_id, current_user.id)
    if items is None:
        raise HTTPException(status_code=403, detail="No tienes acceso a este préstamo")
    return items


