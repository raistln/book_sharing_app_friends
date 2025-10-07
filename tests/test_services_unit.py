"""
Tests unitarios para servicios críticos del sistema de compartir libros.
Estos tests verifican la lógica de negocio de forma aislada.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session

from app.services.auth_service import register_user, authenticate_user, create_user_access_token
from app.services.loan_service import LoanService
from app.models.user import User
from app.models.book import Book, BookStatus
from app.models.loan import Loan, LoanStatus
from app.schemas.user import UserCreate
from fastapi import HTTPException


class TestAuthService:
    """Tests unitarios para el servicio de autenticación."""
    
    def test_register_user_success(self):
        """Test registro exitoso de usuario."""
        # Mock de la sesión de base de datos
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Datos del usuario
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123!",
            full_name="Test User"
        )
        
        # Ejecutar registro
        with patch('app.services.auth_service.hash_password', return_value="hashed_password"), \
             patch('app.services.auth_service.logger') as mock_logger:
            # Mock logger handlers to have real level
            mock_handler = Mock()
            mock_handler.level = 10  # DEBUG level as int
            mock_logger.handlers = [mock_handler]
            result = register_user(db=mock_db, user_in=user_data)
        
        # Verificaciones
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, User)
        assert result.username == "testuser"
        assert result.email == "test@example.com"
    
    def test_register_user_duplicate_username(self):
        """Test registro con username duplicado."""
        mock_db = Mock(spec=Session)
        existing_user = User(username="testuser", email="other@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123!",
            full_name="Test User"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            register_user(db=mock_db, user_in=user_data)
        
        assert exc_info.value.status_code == 400
        assert "username ya está en uso" in exc_info.value.detail
    
    def test_authenticate_user_success(self):
        """Test autenticación exitosa."""
        mock_db = Mock(spec=Session)
    
    def test_authenticate_user_invalid_credentials(self):
        """Test autenticación con credenciales inválidas."""
        mock_db = Mock(spec=Session)
        mock_user = User(
            username="testuser",
            password_hash="hashed_password",
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=False), \
             patch('app.services.auth_service.logger') as mock_logger:
            # Mock logger handlers
            mock_handler = Mock()
            mock_handler.level = 10
            mock_logger.handlers = [mock_handler]
            result = authenticate_user(db=mock_db, username="testuser", password="wrongpassword")
        
        assert result is None
    
    def test_authenticate_user_inactive(self):
        """Test autenticación con usuario inactivo."""
        mock_db = Mock(spec=Session)
        mock_user = User(
            username="testuser",
            password_hash="hashed_password",
            is_active=False
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=True), \
             patch('app.services.auth_service.logger') as mock_logger:
            # Mock logger handlers
            mock_handler = Mock()
            mock_handler.level = 10
            mock_logger.handlers = [mock_handler]
            result = authenticate_user(db=mock_db, username="testuser", password="password123")
        
        assert result is None
    
    def test_create_user_access_token(self):
        """Test creación de token de acceso."""
        user = User(id=uuid4(), username="testuser")
        
        with patch('app.services.auth_service.create_access_token', return_value="mock_token") as mock_create:
            result = create_user_access_token(user)
            
            mock_create.assert_called_once_with(subject=str(user.id))
            assert result == "mock_token"


class TestLoanService:
    """Tests unitarios para el servicio de préstamos."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock(spec=Session)
        self.loan_service = LoanService(self.mock_db)
        
        # Datos de prueba
        self.book_id = uuid4()
        self.borrower_id = uuid4()
        self.lender_id = uuid4()
        self.loan_id = uuid4()
    
    def test_request_loan_success(self):
        """Test solicitud exitosa de préstamo."""
        # Mock del libro disponible
        mock_book = Book(
            id=self.book_id,
            owner_id=self.lender_id,
            status=BookStatus.available,
            is_archived=False
        )
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_book,  # Primera consulta: libro existe
            None        # Segunda consulta: no hay préstamo existente
        ]
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # Ejecutar solicitud
        with patch('app.services.loan_service.logger') as mock_logger:
            # Mock logger handlers
            mock_handler = Mock()
            mock_handler.level = 10
            mock_logger.handlers = [mock_handler]
            result = self.loan_service.request_loan(self.book_id, self.borrower_id)
        
        # Verificaciones
        assert isinstance(result, Loan)
        assert result.book_id == self.book_id
        assert result.borrower_id == self.borrower_id
        assert result.lender_id == self.lender_id
        assert result.status == LoanStatus.requested
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
    
    def test_request_loan_book_not_found(self):
        """Test solicitud con libro inexistente."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.loan_service.request_loan(self.book_id, self.borrower_id)
        
        assert result is None
    
    def test_request_loan_book_already_loaned(self):
        """Test solicitud con libro ya prestado."""
        mock_book = Book(
            id=self.book_id,
            owner_id=self.lender_id,
            status=BookStatus.loaned,
            is_archived=False
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_book
        
        result = self.loan_service.request_loan(self.book_id, self.borrower_id)
        
        assert result is None
    
    def test_approve_loan_success(self):
        """Test aprobación exitosa de préstamo."""
        # Mock del préstamo y libro
        mock_loan = Loan(
            id=self.loan_id,
            book_id=self.book_id,
            borrower_id=self.borrower_id,
            lender_id=self.lender_id,
            status=LoanStatus.requested
        )
        mock_book = Book(
            id=self.book_id,
            status=BookStatus.available
        )
        
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_loan,  # Primera consulta: préstamo existe
            mock_book   # Segunda consulta: libro disponible
        ]
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        due_date = datetime.now(timezone.utc) + timedelta(days=14)
        result = self.loan_service.approve_loan(self.loan_id, self.lender_id, due_date)
        
        # Verificaciones
        assert result == mock_loan
        assert mock_loan.status == LoanStatus.active
        assert mock_loan.due_date == due_date
        assert mock_book.status == BookStatus.loaned
        assert mock_book.current_borrower_id == self.borrower_id
        self.mock_db.commit.assert_called_once()
    
    def test_approve_loan_unauthorized(self):
        """Test aprobación por usuario no autorizado."""
        mock_loan = Loan(
            id=self.loan_id,
            lender_id=uuid4(),  # Diferente al lender_id del test
            status=LoanStatus.requested
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_loan
        
        result = self.loan_service.approve_loan(self.loan_id, self.lender_id)
        
        assert result is None
    
    def test_return_book_success(self):
        """Test devolución exitosa de libro."""
        mock_book = Book(
            id=self.book_id,
            status=BookStatus.loaned,
            current_borrower_id=self.borrower_id
        )
        mock_loan = Loan(
            book_id=self.book_id,
            status=LoanStatus.active
        )
        
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_book,  # Primera consulta: libro prestado
            mock_loan   # Segunda consulta: préstamo activo
        ]
        self.mock_db.commit = Mock()
        
        result = self.loan_service.return_book(self.book_id)
        
        # Verificaciones
        assert result is True
        assert mock_book.status == BookStatus.available
        assert mock_book.current_borrower_id is None
        assert mock_loan.status == LoanStatus.returned
        assert mock_loan.returned_at is not None
        self.mock_db.commit.assert_called_once()
    
    def test_return_book_not_loaned(self):
        """Test devolución de libro no prestado."""
        mock_book = Book(
            id=self.book_id,
            status=BookStatus.available
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_book
        
        result = self.loan_service.return_book(self.book_id)
        
        assert result is False
    
    def test_reject_loan_success(self):
        """Test rechazo exitoso de préstamo."""
        mock_loan = Loan(
            id=self.loan_id,
            lender_id=self.lender_id,
            status=LoanStatus.requested
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_loan
        self.mock_db.delete = Mock()
        self.mock_db.commit = Mock()
        
        result = self.loan_service.reject_loan(self.loan_id, self.lender_id)
        
        assert result is True
        self.mock_db.delete.assert_called_once_with(mock_loan)
        self.mock_db.commit.assert_called_once()
    
    def test_set_due_date_success(self):
        """Test establecimiento exitoso de fecha de vencimiento."""
        mock_loan = Loan(
            id=self.loan_id,
            lender_id=self.lender_id,
            status=LoanStatus.active
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_loan
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        new_due_date = datetime.now(timezone.utc) + timedelta(days=30)
        result = self.loan_service.set_due_date(self.loan_id, self.lender_id, new_due_date)
        
        assert result == mock_loan
        assert mock_loan.due_date == new_due_date
        self.mock_db.commit.assert_called_once()
