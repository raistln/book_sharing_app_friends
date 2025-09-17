import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.book import Book
from app.models.user import User


def _register_and_login(client: TestClient):
    """Helper function to register a user and log them in"""
    username = f"bkl_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"

    # Register user
    r = client.post(
        "/auth/register",
        json={"username": username, "password": password, "email": email}
    )
    assert r.status_code == 201, f"Failed to register user: {r.text}"
    user = r.json()

    # Login
    r = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Failed to login: {r.text}"
    token = r.json()["access_token"]
    return user, token


def test_books_crud_and_loan_flow():
    c = TestClient(app)

    # Usuario owner
    owner, owner_token = _register_and_login(c)
    # Usuario borrower
    borrower, borrower_token = _register_and_login(c)

    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Create book payload with all required fields
    book_payload = {
        "title": "El Quijote",
        "author": "Cervantes",
        "isbn": "9788491050290",
        "description": "Clásico",
        "owner_id": owner["id"],
        "is_archived": False,  # Explicitly set to false
        "status": "available",  # Explicitly set status
        "book_type": "novel",  # Add required field
        "genre": "fiction"  # Add required field
    }
    # Create book
    r = c.post("/books/", json=book_payload, headers=owner_headers)
    assert r.status_code == 201, f"Failed to create book: {r.text}"
    book = r.json()
    print(f"\n=== DEBUG: Book created ===")
    print(f"Book ID: {book['id']}")
    print(f"Owner ID: {book['owner_id']}")
    print(f"Status: {book.get('status')}")
    print(f"Is Archived: {book.get('is_archived', 'Not in response')}")
    print("======================\n")
    
    # Verify book details
    assert book["owner_id"] == owner["id"], f"Expected owner_id {owner['id']}, got {book['owner_id']}"
    assert book["status"] == "available", f"Expected status 'available', got {book['status']}"

    # Verify the book is not archived and is available
    assert not book.get("is_archived", True), f"Book was created as archived: {book}"
    assert book.get("status") == "available", f"Book status is not 'available': {book}"

    # List all books and verify the book is present
    r = c.get("/books/")
    assert r.status_code == 200, f"Failed to list books: {r.text}"
    all_books = r.json()
    print(f"\n=== DEBUG: All books ===")
    for b in all_books:
        print(f"Book ID: {b['id']}, Title: {b['title']}, Archived: {b.get('is_archived', 'N/A')}")
    print("====================\n")
    
    # Verify the book is in the list
    assert any(b["id"] == book["id"] for b in all_books), "Book not found in the list of all books"

    # Prestar libro al borrower
    r = c.post(
        "/loans/loan",
        params={"book_id": book["id"], "borrower_id": borrower["id"]},
    )
    assert r.status_code == 201, r.text

    # Listar libros disponibles (debería estar el recién creado)
    print("\n=== DEBUG: Listing all books ===")
    r = c.get("/books/")
    print(f"Status code: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 200, f"Failed to list books: {r.text}"
    books = r.json()
    print(f"Books found: {len(books)}")
    for i, book in enumerate(books, 1):
        print(f"Book {i}: {book}")
    assert len(books) > 0, "No se encontraron libros disponibles"

    # Verificar estado del libro prestado
    r = c.get(f"/books/{book['id']}")
    assert r.status_code == 200
    book_after = r.json()
    assert book_after["status"] == "loaned"
    assert book_after["current_borrower_id"] == borrower["id"]

    # Devolver libro
    r = c.post("/loans/return", params={"book_id": book["id"]})
    assert r.status_code == 200

    r = c.get(f"/books/{book['id']}")
    assert r.status_code == 200
    book_final = r.json()
    assert book_final["status"] == "available"
    assert book_final["current_borrower_id"] is None


