"""
Servicio de chat por préstamo: enviar y listar mensajes, y limpieza.
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta

from app.models.message import Message as MessageModel
from app.models.loan import Loan as LoanModel


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def can_access(self, loan_id, user_id) -> bool:
        loan = self.db.query(LoanModel).filter(LoanModel.id == loan_id).first()
        if not loan:
            return False
        return loan.borrower_id == user_id or loan.lender_id == user_id

    def send(self, loan_id, sender_id, content: str) -> MessageModel | None:
        if not self.can_access(loan_id, sender_id):
            return None
        msg = MessageModel(loan_id=loan_id, sender_id=sender_id, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_for_loan(self, loan_id, user_id) -> List[MessageModel] | None:
        if not self.can_access(loan_id, user_id):
            return None
        return self.db.query(MessageModel).filter(MessageModel.loan_id == loan_id).order_by(MessageModel.created_at.asc()).all()

    def cleanup_older_than(self, days: int) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        # borrado por lotes simple
        q = self.db.query(MessageModel).filter(MessageModel.created_at < cutoff)
        count = q.count()
        q.delete(synchronize_session=False)
        self.db.commit()
        return count


