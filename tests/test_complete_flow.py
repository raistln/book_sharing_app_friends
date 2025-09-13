"""
Test de flujo completo: registro → añadir libro → préstamo.
Este test verifica la integración completa del sistema desde el registro de usuarios
hasta el proceso completo de préstamo de libros.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app


class TestCompleteUserFlow:
    """Test del flujo completo de usuario en el sistema."""
    
    def test_complete_book_sharing_flow(self):
        """
        Test del flujo completo:
        1. Registro de dos usuarios (lender y borrower)
        2. Login de ambos usuarios
        3. Lender añade un libro a su biblioteca
        4. Borrower busca y encuentra el libro
        5. Borrower solicita préstamo del libro
        6. Lender aprueba el préstamo
        7. Verificación del estado del préstamo
        8. Devolución del libro
        9. Verificación del estado final
        """
        client = TestClient(app)
        
        # === FASE 1: REGISTRO DE USUARIOS ===
        
        # Generar datos únicos
        lender_username = f"lender_{uuid.uuid4().hex[:8]}"
        borrower_username = f"borrower_{uuid.uuid4().hex[:8]}"
        
        # Registro del propietario del libro (lender)
        lender_data = {
            "username": lender_username,
            "email": f"{lender_username}@example.com",
            "password": "LenderPassword123!",
            "full_name": "Book Lender User",
            "bio": "I love sharing my books with friends"
        }
        
        response = client.post("/auth/register", json=lender_data)
        assert response.status_code == 201
        lender_info = response.json()
        lender_id = lender_info["id"]
        
        # Registro del solicitante (borrower)
        borrower_data = {
            "username": borrower_username,
            "email": f"{borrower_username}@example.com",
            "password": "BorrowerPassword123!",
            "full_name": "Book Borrower User",
            "bio": "Always looking for good books to read"
        }
        
        response = client.post("/auth/register", json=borrower_data)
        assert response.status_code == 201
        borrower_info = response.json()
        borrower_id = borrower_info["id"]
        
        # === FASE 2: LOGIN DE USUARIOS ===
        
        # Login del lender
        lender_login = {
            "username": lender_username,
            "password": "LenderPassword123!"
        }
        response = client.post(
            "/auth/login",
            data=lender_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        lender_token = response.json()["access_token"]
        lender_headers = {"Authorization": f"Bearer {lender_token}"}
        
        # Login del borrower
        borrower_login = {
            "username": borrower_username,
            "password": "BorrowerPassword123!"
        }
        response = client.post(
            "/auth/login",
            data=borrower_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        borrower_token = response.json()["access_token"]
        borrower_headers = {"Authorization": f"Bearer {borrower_token}"}
        
        # === FASE 3: LENDER AÑADE LIBRO ===
        
        book_data = {
            "title": "The Complete Guide to Book Sharing",
            "author": "Jane Bookworm",
            "isbn": "9781234567890",
            "description": "A comprehensive guide to sharing books among friends and building a community of readers.",
            "genre": "self_help",
            "publication_year": 2023,
            "condition": "excellent",
            "location": "Living room bookshelf"
        }
        
        response = client.post("/books/", json=book_data, headers=lender_headers)
        assert response.status_code == 201
        created_book = response.json()
        book_id = created_book["id"]
        
        # Verificar que el libro fue creado correctamente
        assert created_book["title"] == book_data["title"]
        assert created_book["author"] == book_data["author"]
        assert created_book["owner_id"] == lender_id
        assert created_book["status"] == "available"
        
        # === FASE 4: BORROWER BUSCA LIBROS ===
        
        # Listar todos los libros disponibles (simulando búsqueda)
        response = client.get("/books/", headers=borrower_headers)
        assert response.status_code == 200
        available_books = response.json()
        
        # Verificar que el libro del lender aparece en la lista
        book_found = False
        for book in available_books:
            if book["id"] == book_id:
                book_found = True
                assert book["title"] == book_data["title"]
                assert book["status"] == "available"
                break
        
        assert book_found, "El libro del lender debería aparecer en la lista de libros disponibles"
        
        # === FASE 5: BORROWER SOLICITA PRÉSTAMO ===
        
        response = client.post(
            f"/loans/request?book_id={book_id}&borrower_id={borrower_id}",
            headers=borrower_headers
        )
        assert response.status_code == 201
        loan_request = response.json()
        loan_id = loan_request["loan_id"]
        
        # === FASE 6: LENDER VE Y APRUEBA EL PRÉSTAMO ===
        
        # Lender consulta sus préstamos pendientes
        response = client.get("/loans/", headers=lender_headers)
        assert response.status_code == 200
        lender_loans = response.json()
        
        # Verificar que la solicitud aparece en los préstamos del lender
        loan_found = False
        for loan in lender_loans:
            if loan["id"] == loan_id:
                loan_found = True
                assert loan["status"] == "requested"
                break
        
        assert loan_found, "La solicitud de préstamo debería aparecer en la lista del lender"
        
        # Lender aprueba el préstamo
        response = client.post(
            f"/loans/{loan_id}/approve?lender_id={lender_id}",
            headers=lender_headers
        )
        assert response.status_code == 200
        approved_loan = response.json()
        
        # Verificar que el préstamo fue aprobado
        assert approved_loan["status"] == "active"
        assert approved_loan["loan_id"] is not None
        
        # === FASE 7: VERIFICACIÓN DEL ESTADO DEL PRÉSTAMO ===
        
        # Verificar que el libro ahora está prestado
        response = client.get(f"/books/{book_id}", headers=lender_headers)
        assert response.status_code == 200
        loaned_book = response.json()
        
        assert loaned_book["status"] == "loaned"
        assert loaned_book["current_borrower_id"] == borrower_id
        
        # Borrower verifica que tiene el libro prestado
        response = client.get("/loans/", headers=borrower_headers)
        assert response.status_code == 200
        borrower_loans = response.json()
        
        active_loan_found = False
        for loan in borrower_loans:
            if loan["id"] == loan_id and loan["status"] == "active":
                active_loan_found = True
                assert loan["book"]["id"] == book_id
                break
        
        assert active_loan_found, "El borrower debería tener un préstamo activo"
        
        # === FASE 8: DEVOLUCIÓN DEL LIBRO ===
        
        # Lender procesa la devolución del libro
        response = client.post(
            f"/loans/return?book_id={book_id}",
            headers=lender_headers
        )
        assert response.status_code == 200
        return_result = response.json()
        
        assert return_result["message"] == "Libro devuelto exitosamente"
        
        # === FASE 9: VERIFICACIÓN DEL ESTADO FINAL ===
        
        # Verificar que el libro está disponible nuevamente
        response = client.get(f"/books/{book_id}", headers=lender_headers)
        assert response.status_code == 200
        returned_book = response.json()
        
        assert returned_book["status"] == "available"
        assert returned_book["current_borrower_id"] is None
        
        # Verificar el historial del préstamo
        response = client.get(f"/loans/history/book/{book_id}", headers=lender_headers)
        assert response.status_code == 200
        loan_history = response.json()
        
        assert len(loan_history) >= 1
        completed_loan = loan_history[0]  # El más reciente
        assert completed_loan["status"] == "returned"
        assert completed_loan["returned_at"] is not None
        
        # === VERIFICACIÓN FINAL: INTEGRIDAD DEL SISTEMA ===
        
        # Verificar que ambos usuarios pueden ver el historial correctamente
        response = client.get("/loans/", headers=lender_headers)
        assert response.status_code == 200
        final_lender_loans = response.json()
        
        response = client.get("/loans/", headers=borrower_headers)
        assert response.status_code == 200
        final_borrower_loans = response.json()
        
        # Ambos deberían tener registro del préstamo completado
        lender_has_completed_loan = any(
            loan["id"] == loan_id and loan["status"] == "returned"
            for loan in final_lender_loans
        )
        borrower_has_completed_loan = any(
            loan["id"] == loan_id and loan["status"] == "returned"
            for loan in final_borrower_loans
        )
        
        assert lender_has_completed_loan, "Lender debería tener registro del préstamo completado"
        assert borrower_has_completed_loan, "Borrower debería tener registro del préstamo completado"
    
    def test_loan_rejection_flow(self):
        """
        Test del flujo de rechazo de préstamo:
        1. Setup inicial (usuarios y libro)
        2. Solicitud de préstamo
        3. Rechazo del préstamo
        4. Verificación del estado
        """
        client = TestClient(app)
        
        # Setup inicial similar al test anterior (simplificado)
        lender_username = f"lender_reject_{uuid.uuid4().hex[:8]}"
        borrower_username = f"borrower_reject_{uuid.uuid4().hex[:8]}"
        
        # Registro y login de usuarios (código simplificado)
        lender_data = {
            "username": lender_username,
            "email": f"{lender_username}@example.com",
            "password": "Password123!",
            "full_name": "Lender User"
        }
        response = client.post("/auth/register", json=lender_data)
        assert response.status_code == 201
        lender_id = response.json()["id"]
        
        borrower_data = {
            "username": borrower_username,
            "email": f"{borrower_username}@example.com",
            "password": "Password123!",
            "full_name": "Borrower User"
        }
        response = client.post("/auth/register", json=borrower_data)
        assert response.status_code == 201
        borrower_id = response.json()["id"]
        
        # Login de usuarios
        for username, user_type in [(lender_username, "lender"), (borrower_username, "borrower")]:
            login_data = {"username": username, "password": "Password123!"}
            response = client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            if user_type == "lender":
                lender_headers = {"Authorization": f"Bearer {token}"}
            else:
                borrower_headers = {"Authorization": f"Bearer {token}"}
        
        # Crear libro
        book_data = {
            "title": "Book for Rejection Test",
            "author": "Test Author",
            "isbn": "9780987654321"
        }
        response = client.post("/books/", json=book_data, headers=lender_headers)
        assert response.status_code == 201
        book_id = response.json()["id"]
        
        # Solicitar préstamo (usando request para mantenerlo en estado "requested")
        response = client.post(
            f"/loans/request?book_id={book_id}&borrower_id={borrower_id}",
            headers=borrower_headers
        )
        assert response.status_code == 201
        loan_data = response.json()
        loan_id = loan_data["loan_id"]
        
        # Rechazar préstamo
        response = client.post(f"/loans/{loan_id}/reject?lender_id={lender_id}", headers=lender_headers)
        assert response.status_code == 200
        
        # Verificar que el libro sigue disponible
        response = client.get(f"/books/{book_id}", headers=lender_headers)
        assert response.status_code == 200
        book_status = response.json()
        assert book_status["status"] == "available"
        
        # Verificar que la solicitud ya no existe en préstamos activos
        response = client.get("/loans/", headers=lender_headers)
        assert response.status_code == 200
        loans = response.json()
        
        active_loan_exists = any(
            loan["id"] == loan_id and loan["status"] in ["requested", "active"]
            for loan in loans
        )
        assert not active_loan_exists, "No debería existir préstamo activo después del rechazo"
