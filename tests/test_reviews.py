"""
Pruebas para endpoints de Reviews (Reseñas)
"""
import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.book import Book, BookType, BookGenre, BookStatus
from app.models.user import User
from app.models.review import Review
from app.models.group import Group, GroupRole
import pytest


def _register_and_login(client: TestClient):
    """Helper function to register a user and log them in"""
    username = f"rvw_{uuid.uuid4().hex[:8]}"
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


def _create_test_book(client: TestClient, token: str, owner_id: UUID = None):
    """Helper function to create a test book"""
    headers = {"Authorization": f"Bearer {token}"}
    book_data = {
        "title": "Test Book for Review",
        "author": "Test Author",
        "isbn": "1234567890123",
        "description": "A test book for review testing",
        "book_type": "novel",
        "genre": "science_fiction",
        "is_archived": False
    }

    if owner_id:
        book_data["owner_id"] = str(owner_id)

    r = client.post("/books/", json=book_data, headers=headers)
    assert r.status_code == 201, f"Failed to create book: {r.text}"
    return r.json()


def _create_test_user(db_session):
    """Helper function to create a test user in the database"""
    user = User(
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_test_book_in_db(db_session, owner_id: UUID):
    """Helper function to create a test book in the database"""
    book = Book(
        title="Test Book for Review DB",
        author="Test Author DB",
        isbn="1234567890124",
        description="A test book for review testing in DB",
        book_type=BookType.novel,
        genre=BookGenre.science_fiction,
        owner_id=owner_id,
        status=BookStatus.available,
        is_archived=False
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book


def test_create_review_success():
    """Test creating a review successfully"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    book = _create_test_book(c, token, user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {
        "rating": 5,
        "comment": "Excellent book!",
        "book_id": book["id"]
    }

    r = c.post("/reviews/", json=review_data, headers=headers)
    assert r.status_code == 201, f"Failed to create review: {r.text}"
    review = r.json()
    assert review["rating"] == 5
    assert review["comment"] == "Excellent book!"
    assert review["book_id"] == book["id"]
    assert review["user_id"] == user["id"]
    assert "book_title" in review
    assert "user_username" in review


def test_create_review_book_not_found():
    """Test creating a review for non-existent book"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {
        "rating": 4,
        "comment": "Good book",
        "book_id": str(uuid.uuid4())  # Non-existent book ID
    }

    r = c.post("/reviews/", json=review_data, headers=headers)
    assert r.status_code == 404, f"Expected 404 for non-existent book: {r.text}"


def test_create_review_duplicate():
    """Test creating a duplicate review for the same book"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    book = _create_test_book(c, token, user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {
        "rating": 4,
        "comment": "First review",
        "book_id": book["id"]
    }

    # Create first review
    r1 = c.post("/reviews/", json=review_data, headers=headers)
    assert r1.status_code == 201

    # Try to create second review for same book
    r2 = c.post("/reviews/", json=review_data, headers=headers)
    assert r2.status_code == 400, f"Expected 400 for duplicate review: {r2.text}"


def test_list_reviews():
    """Test listing reviews with filters"""
    c = TestClient(app)

    # Create users and books
    user1, token1 = _register_and_login(c)
    user2, token2 = _register_and_login(c)
    book1 = _create_test_book(c, token1, user1["id"])
    book2 = _create_test_book(c, token2, user2["id"])

    # Create reviews
    review1_data = {"rating": 5, "comment": "Review 1", "book_id": book1["id"]}
    review2_data = {"rating": 3, "comment": "Review 2", "book_id": book2["id"]}

    c.post("/reviews/", json=review1_data, headers={"Authorization": f"Bearer {token1}"})
    c.post("/reviews/", json=review2_data, headers={"Authorization": f"Bearer {token2}"})

    # Test listing all reviews
    r = c.get("/reviews/")
    assert r.status_code == 200
    reviews = r.json()
    assert len(reviews) >= 2

    # Test filtering by book_id
    r = c.get(f"/reviews/?book_id={book1['id']}")
    assert r.status_code == 200
    filtered_reviews = r.json()
    assert len(filtered_reviews) == 1
    assert filtered_reviews[0]["book_id"] == book1["id"]


def test_get_review():
    """Test getting a single review"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    book = _create_test_book(c, token, user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {"rating": 4, "comment": "Test review", "book_id": book["id"]}
    create_r = c.post("/reviews/", json=review_data, headers=headers)
    review = create_r.json()

    # Get the review
    r = c.get(f"/reviews/{review['id']}")
    assert r.status_code == 200
    fetched_review = r.json()
    assert fetched_review["id"] == review["id"]
    assert fetched_review["rating"] == 4


def test_update_review():
    """Test updating a review"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    book = _create_test_book(c, token, user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {"rating": 3, "comment": "Original comment", "book_id": book["id"]}
    create_r = c.post("/reviews/", json=review_data, headers=headers)
    review = create_r.json()

    # Update the review
    update_data = {"rating": 5, "comment": "Updated comment"}
    r = c.put(f"/reviews/{review['id']}", json=update_data, headers=headers)
    assert r.status_code == 200
    updated_review = r.json()
    assert updated_review["rating"] == 5
    assert updated_review["comment"] == "Updated comment"


def test_update_review_unauthorized():
    """Test updating a review without authorization"""
    c = TestClient(app)
    user1, token1 = _register_and_login(c)
    user2, token2 = _register_and_login(c)
    book = _create_test_book(c, token1, user1["id"])
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    review_data = {"rating": 3, "comment": "Test review", "book_id": book["id"]}
    create_r = c.post("/reviews/", json=review_data, headers=headers1)
    review = create_r.json()

    # Try to update with different user
    update_data = {"rating": 5}
    r = c.put(f"/reviews/{review['id']}", json=update_data, headers=headers2)
    assert r.status_code == 403, f"Expected 403 for unauthorized update: {r.text}"


def test_delete_review():
    """Test deleting a review"""
    c = TestClient(app)
    user, token = _register_and_login(c)
    book = _create_test_book(c, token, user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    review_data = {"rating": 4, "comment": "Review to delete", "book_id": book["id"]}
    create_r = c.post("/reviews/", json=review_data, headers=headers)
    review = create_r.json()

    # Delete the review
    r = c.delete(f"/reviews/{review['id']}", headers=headers)
    assert r.status_code == 204

    # Verify it's deleted
    get_r = c.get(f"/reviews/{review['id']}")
    assert get_r.status_code == 404


def test_delete_review_unauthorized():
    """Test deleting a review without authorization"""
    c = TestClient(app)
    user1, token1 = _register_and_login(c)
    user2, token2 = _register_and_login(c)
    book = _create_test_book(c, token1, user1["id"])
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    review_data = {"rating": 3, "comment": "Test review", "book_id": book["id"]}
    create_r = c.post("/reviews/", json=review_data, headers=headers1)
    review = create_r.json()

    # Try to delete with different user
    r = c.delete(f"/reviews/{review['id']}", headers=headers2)
    assert r.status_code == 403, f"Expected 403 for unauthorized delete: {r.text}"
