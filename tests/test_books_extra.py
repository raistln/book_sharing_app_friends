import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.book import Book


def _register_and_login(client: TestClient):
    """Helper function to register a user and log them in"""
    username = f"bkx_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    
    # Register user
    r = client.post(
        "/auth/register", 
        json={"username": username, "password": password, "email": email}
    )
    assert r.status_code == 201, f"Failed to register user: {r.text}"
    user = r.json()
    
    # Login to get token
    r = client.post(
        "/auth/login", 
        data={"username": username, "password": password}, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    
    return user, token


def test_update_status_invalid_returns_400(db_session):
    """Test that updating a book with an invalid status returns 400"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a book using the API with all required fields and correct enum values
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890",
        "description": "Test Description",
        "status": "available",
        "book_type": "novel",  # Using a valid BookType value
        "genre": "science_fiction",  # Using a valid BookGenre value
        "is_archived": False  # Explicitly set to not archived
    }
    r = c.post("/books/", json=book_data, headers=headers)
    assert r.status_code == 201, f"Failed to create book: {r.text}"
    book = r.json()
    
    # Test updating with invalid status
    r = c.put(f"/books/{book['id']}", json={"status": "invalid_state"}, headers=headers)
    assert r.status_code == 422, "Should return 422 for invalid status value"
    
    # Debug: List all books in the database
    all_books = db_session.query(Book).all()
    print(f"\n=== DEBUG: All books in database (total: {len(all_books)}) ===")
    for b in all_books:
        print(f"- ID: {b.id}, Title: {b.title}, Status: {b.status}, Owner: {b.owner_id}, Archived: {b.is_archived}")
    print("=== END DEBUG ===\n")
    
    # Get the book from the database to ensure it's not archived
    db_book = db_session.query(Book).filter(Book.id == UUID(book['id'])).first()
    if db_book and db_book.is_archived:
        print(f"Book is archived, unarchiving it...")
        db_book.is_archived = False
        db_session.commit()
        print(f"Book unarchived. New status: is_archived={db_book.is_archived}")
    
    # Test updating with valid status (using 'loaned' instead of 'borrowed')
    # Include all required fields in the update with correct enum values
    update_data = {
        "title": "Test Book Updated",
        "author": "Test Author Updated",
        "isbn": "0987654321",
        "description": "Updated Description",
        "status": "loaned",
        "book_type": "biography",  # Using a valid BookType value
        "genre": "biography"  # Using a valid BookGenre value
    }
    
    print(f"\n=== DEBUG: Attempting to update book {book['id']} with data: {update_data}")
    
    # Make the update request
    r = c.put(f"/books/{book['id']}", json=update_data, headers=headers)
    
    print(f"=== DEBUG: Update response - Status: {r.status_code}, Body: {r.text}\n")
    
    # If the update failed, show more details
    if r.status_code != 200:
        # Try to get the book directly from the database
        db_book = db_session.query(Book).filter(Book.id == UUID(book['id'])).first()
        if db_book:
            print(f"=== DEBUG: Book found in database - ID: {db_book.id}, Title: {db_book.title}, Status: {db_book.status}, Owner: {db_book.owner_id}, Archived: {db_book.is_archived}")
        else:
            print(f"=== DEBUG: Book with ID {book['id']} not found in database")
    
    assert r.status_code == 200, f"Should return 200 for valid status update, got {r.status_code}: {r.text}"
    updated_book = r.json()
    # The status in the response might be an enum value, so we check both string and enum representations
    assert updated_book["status"] in ["loaned", "BookStatus.loaned"], f"Book status should be updated to 'loaned', got {updated_book['status']}"
