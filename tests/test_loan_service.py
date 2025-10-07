"""
Pruebas unitarias para LoanService
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.loan_service import LoanService
from app.models.book import Book as BookModel, BookStatus
from app.models.loan import Loan as LoanModel, LoanStatus
from datetime import datetime, timezone, timedelta


class TestLoanService:
    def test_request_loan(self):
        """Test request_loan"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        book_id = "550e8400-e29b-41d4-a716-446655440000"
        borrower_id = "550e8400-e29b-41d4-a716-446655440001"

        mock_book = MagicMock()
        mock_book.status = BookStatus.available
        mock_book.id = book_id
        mock_book.owner_id = "550e8400-e29b-41d4-a716-446655440002"

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [mock_book, None]  # Book exists, no existing loan

        mock_loan = MagicMock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        result = service.request_loan(book_id, borrower_id)

        assert result is not None

    def test_approve_loan(self):
        """Test approve_loan"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        loan_id = "550e8400-e29b-41d4-a716-446655440000"
        lender_id = "550e8400-e29b-41d4-a716-446655440001"
        due_date = datetime.now(timezone.utc) + timedelta(days=7)

        mock_loan = MagicMock()
        mock_loan.lender_id = lender_id
        mock_loan.status = LoanStatus.requested

        mock_book = MagicMock()
        mock_book.status = BookStatus.available

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [mock_loan, mock_book]

        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        result = service.approve_loan(loan_id, lender_id, due_date)

        assert result is not None
        assert mock_loan.status == LoanStatus.active

    def test_reject_loan(self):
        """Test reject_loan"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        loan_id = "550e8400-e29b-41d4-a716-446655440000"
        lender_id = "550e8400-e29b-41d4-a716-446655440001"

        mock_loan = MagicMock()
        mock_loan.lender_id = lender_id
        mock_loan.status = LoanStatus.requested

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_loan

        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        result = service.reject_loan(loan_id, lender_id)

        assert result == True

    def test_return_book(self):
        """Test return_book"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        book_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_book = MagicMock()
        mock_book.status = BookStatus.loaned

        mock_loan = MagicMock()
        mock_loan.status = LoanStatus.active

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [mock_book, mock_loan]

        mock_db.commit.return_value = None

        result = service.return_book(book_id)

        assert result == True
        assert mock_book.status == BookStatus.available

    def test_set_due_date(self):
        """Test set_due_date"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        loan_id = "550e8400-e29b-41d4-a716-446655440000"
        lender_id = "550e8400-e29b-41d4-a716-446655440001"
        due_date = datetime.now(timezone.utc) + timedelta(days=14)

        mock_loan = MagicMock()
        mock_loan.lender_id = lender_id
        mock_loan.status = LoanStatus.active

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_loan

        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        result = service.set_due_date(loan_id, lender_id, due_date)

        assert result is not None
        assert mock_loan.due_date == due_date

    def test_get_user_loans(self):
        """Test get_user_loans"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_loans = [MagicMock(), MagicMock()]

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_loans

        result = service.get_user_loans(user_id)

        assert len(result) == 2

    def test_get_book_history(self):
        """Test get_book_history"""
        mock_db = MagicMock()
        service = LoanService(mock_db)

        book_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_loans = [MagicMock(), MagicMock()]

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_loans

        result = service.get_book_history(book_id)

        assert len(result) == 2
