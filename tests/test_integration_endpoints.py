"""
Tests de integración para endpoints principales.
Estos tests verifican el funcionamiento completo de los endpoints con la base de datos.
"""
import pytest
import uuid
from httpx import AsyncClient, Client
from fastapi.testclient import TestClient
from app.main import app


class TestAuthEndpointsIntegration:
    """Tests de integración para endpoints de autenticación."""
    
    def test_complete_auth_flow(self):
        """Test del flujo completo de autenticación: registro → login → acceso protegido."""
        client = TestClient(app)
        
        # Generar datos únicos para evitar conflictos
        username = f"integtest_{uuid.uuid4().hex[:8]}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        # 1. Registro de usuario
        register_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": "Integration Test User"
        }
        
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["username"] == username
        assert user_data["email"] == email
        assert user_data["is_active"] is True
        assert "id" in user_data
        
        # 2. Login con credenciales
        login_data = {
            "username": username,
            "password": password
        }
        
        response = client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        access_token = token_data["access_token"]
        
        # 3. Acceso a endpoint protegido
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        me_data = response.json()
        assert me_data["username"] == username
        assert me_data["email"] == email
        assert me_data["id"] == user_data["id"]
    
    def test_register_duplicate_username(self):
        """Test registro con username duplicado."""
        client = TestClient(app)
        
        username = f"duplicate_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword123!"
        }
        
        # Primer registro - debe ser exitoso
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Segundo registro con mismo username - debe fallar
        user_data["email"] = f"different_{username}@example.com"
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "username ya está en uso" in response.json()["detail"]
    
    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas."""
        client = TestClient(app)
        
        login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        response = client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test acceso a endpoint protegido sin token."""
        client = TestClient(app)
        
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestBooksEndpointsIntegration:
    """Tests de integración para endpoints de libros."""
    
    def setup_method(self):
        """Configuración inicial: crear usuario y obtener token."""
        self.client = TestClient(app)
        
        # Crear usuario de prueba
        username = f"booktest_{uuid.uuid4().hex[:8]}"
        self.user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword123!",
            "full_name": "Book Test User"
        }
        
        # Registro
        response = self.client.post("/auth/register", json=self.user_data)
        assert response.status_code == 201
        self.user_id = response.json()["id"]
        
        # Login y obtener token
        login_data = {
            "username": username,
            "password": "TestPassword123!"
        }
        response = self.client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_and_get_book(self):
        """Test creación y obtención de libro."""
        # Crear libro
        book_data = {
            "title": "Test Book Integration",
            "author": "Test Author",
            "isbn": "9781234567890",
            "description": "A test book for integration testing",
            "genre": "technology"
        }
        
        response = self.client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 201
        created_book = response.json()
        
        assert created_book["title"] == book_data["title"]
        assert created_book["author"] == book_data["author"]
        assert created_book["isbn"] == book_data["isbn"]
        assert created_book["owner_id"] == self.user_id
        assert "id" in created_book
        
        book_id = created_book["id"]
        
        # Obtener libro por ID
        response = self.client.get(f"/books/{book_id}", headers=self.headers)
        assert response.status_code == 200
        retrieved_book = response.json()
        
        assert retrieved_book["id"] == book_id
        assert retrieved_book["title"] == book_data["title"]
        assert retrieved_book["author"] == book_data["author"]
    
    def test_list_user_books(self):
        """Test listado de libros del usuario."""
        # Crear varios libros
        books_data = [
            {"title": "Book 1", "author": "Author 1", "isbn": "9781111111111"},
            {"title": "Book 2", "author": "Author 2", "isbn": "9782222222222"},
            {"title": "Book 3", "author": "Author 3", "isbn": "9783333333333"}
        ]
        
        created_books = []
        for book_data in books_data:
            response = self.client.post("/books/", json=book_data, headers=self.headers)
            assert response.status_code == 201
            created_books.append(response.json())
        
        # Listar libros
        response = self.client.get("/books/", headers=self.headers)
        assert response.status_code == 200
        books_list = response.json()
        
        assert len(books_list) >= 3
        book_titles = [book["title"] for book in books_list]
        for book_data in books_data:
            assert book_data["title"] in book_titles
    
    def test_update_book(self):
        """Test actualización de libro."""
        # Crear libro
        book_data = {
            "title": "Original Title",
            "author": "Original Author",
            "isbn": "9781234567890"
        }
        
        response = self.client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 201
        book_id = response.json()["id"]
        
        # Actualizar libro
        update_data = {
            "title": "Updated Title",
            "author": "Updated Author",
            "description": "Updated description"
        }
        
        response = self.client.put(f"/books/{book_id}", json=update_data, headers=self.headers)
        assert response.status_code == 200
        updated_book = response.json()
        
        assert updated_book["title"] == update_data["title"]
        assert updated_book["author"] == update_data["author"]
        assert updated_book["description"] == update_data["description"]
        assert updated_book["isbn"] == book_data["isbn"]  # No cambiado
    
    def test_delete_book(self):
        """Test eliminación (soft delete) de libro."""
        # Crear libro
        book_data = {
            "title": "Book to Delete",
            "author": "Delete Author",
            "isbn": "9781234567890"
        }
        
        response = self.client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 201
        book_id = response.json()["id"]
        
        # Eliminar libro
        response = self.client.delete(f"/books/{book_id}", headers=self.headers)
        assert response.status_code == 204
        
        # Verificar que no aparece en la lista
        response = self.client.get("/books/", headers=self.headers)
        assert response.status_code == 200
        books_list = response.json()
        
        book_ids = [book["id"] for book in books_list]
        assert book_id not in book_ids
    
    def test_unauthorized_book_operations(self):
        """Test operaciones no autorizadas en libros de otros usuarios."""
        # Crear segundo usuario
        username2 = f"booktest2_{uuid.uuid4().hex[:8]}"
        user2_data = {
            "username": username2,
            "email": f"{username2}@example.com",
            "password": "TestPassword123!",
            "full_name": "Book Test User 2"
        }
        
        response = self.client.post("/auth/register", json=user2_data)
        assert response.status_code == 201
        
        # Login segundo usuario
        login_data = {
            "username": username2,
            "password": "TestPassword123!"
        }
        response = self.client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        token2 = response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Crear libro con primer usuario
        book_data = {
            "title": "Private Book",
            "author": "Private Author",
            "isbn": "9781234567890"
        }
        
        response = self.client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 201
        book_id = response.json()["id"]
        
        # Intentar actualizar con segundo usuario (debe fallar)
        update_data = {"title": "Hacked Title"}
        response = self.client.put(f"/books/{book_id}", json=update_data, headers=headers2)
        assert response.status_code == 403
        
        # Intentar eliminar con segundo usuario (debe fallar)
        response = self.client.delete(f"/books/{book_id}", headers=headers2)
        assert response.status_code == 403


class TestLoansEndpointsIntegration:
    """Tests de integración para endpoints de préstamos."""
    
    def setup_method(self):
        """Configuración inicial: crear dos usuarios y un libro."""
        self.client = TestClient(app)
        
        # Crear primer usuario (propietario del libro)
        username1 = f"lender_{uuid.uuid4().hex[:8]}"
        user1_data = {
            "username": username1,
            "email": f"{username1}@example.com",
            "password": "TestPassword123!",
            "full_name": "Lender User"
        }
        
        response = self.client.post("/auth/register", json=user1_data)
        assert response.status_code == 201
        self.lender_id = response.json()["id"]
        
        # Login primer usuario
        login_data = {"username": username1, "password": "TestPassword123!"}
        response = self.client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        self.lender_token = response.json()["access_token"]
        self.lender_headers = {"Authorization": f"Bearer {self.lender_token}"}
        
        # Crear segundo usuario (solicitante del préstamo)
        username2 = f"borrower_{uuid.uuid4().hex[:8]}"
        user2_data = {
            "username": username2,
            "email": f"{username2}@example.com",
            "password": "TestPassword123!",
            "full_name": "Borrower User"
        }
        
        response = self.client.post("/auth/register", json=user2_data)
        assert response.status_code == 201
        self.borrower_id = response.json()["id"]
        
        # Login segundo usuario
        login_data = {"username": username2, "password": "TestPassword123!"}
        response = self.client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        self.borrower_token = response.json()["access_token"]
        self.borrower_headers = {"Authorization": f"Bearer {self.borrower_token}"}
        
        # Crear libro con primer usuario
        book_data = {
            "title": "Loan Test Book",
            "author": "Loan Author",
            "isbn": "9781234567890"
        }
        
        response = self.client.post("/books/", json=book_data, headers=self.lender_headers)
        assert response.status_code == 201
        self.book_id = response.json()["id"]
    
    def test_complete_loan_flow(self):
        """Test del flujo completo de préstamo: solicitar → aprobar → devolver."""
        # 1. Solicitar préstamo (como borrower)
        response = self.client.post(
            f"/loans/request?book_id={self.book_id}&borrower_id={self.borrower_id}",
            headers=self.borrower_headers
        )
        assert response.status_code == 201
        loan_data = response.json()
        
        assert loan_data["loan_id"] is not None
        loan_id = loan_data["loan_id"]
        
        # 2. Aprobar préstamo (como lender)
        response = self.client.post(
            f"/loans/{loan_id}/approve?lender_id={self.lender_id}",
            headers=self.lender_headers
        )
        assert response.status_code == 200
        approved_loan = response.json()
        
        assert approved_loan["status"] == "active"
        assert approved_loan["loan_id"] is not None
        
        # Verificar que el libro ahora está prestado
        response = self.client.get(f"/books/{self.book_id}", headers=self.lender_headers)
        assert response.status_code == 200
        book_data = response.json()
        assert book_data["status"] == "loaned"
        assert book_data["current_borrower_id"] == self.borrower_id
        
        # 3. Devolver libro
        response = self.client.post(
            f"/loans/return?book_id={self.book_id}",
            headers=self.lender_headers
        )
        assert response.status_code == 200
        
        # Verificar que el libro está disponible nuevamente
        response = self.client.get(f"/books/{self.book_id}", headers=self.lender_headers)
        assert response.status_code == 200
        book_data = response.json()
        assert book_data["status"] == "available"
        assert book_data["current_borrower_id"] is None
    
    def test_loan_unauthorized_operations(self):
        """Test operaciones no autorizadas en préstamos."""
        # Solicitar préstamo
        response = self.client.post(
            f"/loans/request?book_id={self.book_id}&borrower_id={self.borrower_id}",
            headers=self.borrower_headers
        )
        assert response.status_code == 201
        loan_id = response.json()["loan_id"]
        
        # Intentar aprobar como borrower (debe fallar)
        response = self.client.post(
            f"/loans/{loan_id}/approve?lender_id={self.borrower_id}",
            headers=self.borrower_headers
        )
        assert response.status_code == 400  # Business logic error: borrower can't approve their own loan
        
        # Intentar devolver como borrower sin aprobación (debe fallar)
        response = self.client.post(
            f"/loans/return?book_id={self.book_id}",
            headers=self.borrower_headers
        )
        assert response.status_code == 400  # Business logic error: no active loan to return
