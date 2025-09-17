import random
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, Book, Loan


def _register_and_login(c: TestClient):
    u = f"user_{random.randint(100000,999999)}"
    email = f"{u}@example.com"
    r = c.post("/auth/register", json={"username": u, "email": email, "password": "Passw0rd!"})
    assert r.status_code == 201, f"Failed to register user: {r.text}"
    
    r = c.post("/auth/token", data={"username": u, "password": "Passw0rd!"})
    assert r.status_code == 200, f"Failed to get token: {r.text}"
    
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    me = c.get("/users/me", headers=h).json()
    return me, token


def _create_book(c: TestClient, owner_token: str, title="T", author="A"):
    h = {"Authorization": f"Bearer {owner_token}"}
    r = c.post(
        "/books/", 
        json={
            "title": title, 
            "author": author,
            "isbn": "1234567890",
            "description": "Test book",
            "book_type": "novel",
            "genre": "fiction",
            "is_archived": False
        }, 
        headers=h
    )
    assert r.status_code == 201, f"Failed to create book: {r.text}"
    return r.json()


def _loan_book(c: TestClient, book_id: str, borrower_id: str, owner_token: str):
    headers = {"Authorization": f"Bearer {owner_token}"}
    return c.post(
        f"/loans/loan?book_id={book_id}&borrower_id={borrower_id}",
        headers=headers
    )


def test_chat_send_and_receive():
    c = TestClient(app)
    
    # Register and login users
    owner, owner_token = _register_and_login(c)
    borrower, borrower_token = _register_and_login(c)
    
    # Create a book
    book = _create_book(c, owner_token, "ChatBook", "Autor")
    
    # Create a loan
    r = _loan_book(c, book["id"], borrower["id"], owner_token)
    assert r.status_code == 201, f"Failed to create loan: {r.text}"
    loan_id = r.json()["loan_id"]
    
    # Borrower sends a message
    h_b = {"Authorization": f"Bearer {borrower_token}"}
    r = c.post(
        "/chat/send", 
        json={"loan_id": loan_id, "content": "Hola"}, 
        headers=h_b
    )
    assert r.status_code == 201, f"Failed to send message: {r.text}"
    
    # Owner reads messages
    h_o = {"Authorization": f"Bearer {owner_token}"}
    r = c.get(f"/chat/loan/{loan_id}", headers=h_o)
    assert r.status_code == 200, f"Failed to get messages: {r.text}"
    
    msgs = r.json()
    assert len(msgs) >= 1, "No messages found"
    assert msgs[0]["content"] == "Hola", "Message content doesn't match"
    assert msgs[0]["content"] == "Hola"


def test_chat_access_control():
    c = TestClient(app)
    
    # Register and login users
    owner, owner_token = _register_and_login(c)
    borrower, borrower_token = _register_and_login(c)
    other, other_token = _register_and_login(c)
    
    # Create a book
    book = _create_book(c, owner_token, "ChatBook", "Autor")
    
    # Create a loan
    r = _loan_book(c, book["id"], borrower["id"], owner_token)
    assert r.status_code == 201, f"Failed to create loan: {r.text}"
    loan_id = r.json()["loan_id"]
    
    # Other user cannot access the chat
    h_other = {"Authorization": f"Bearer {other_token}"}
    r = c.get(f"/chat/loan/{loan_id}", headers=h_other)
    assert r.status_code == 403, "Other user should not have access to this chat"
    
    # Owner can access the chat
    h_o = {"Authorization": f"Bearer {owner_token}"}
    r = c.get(f"/chat/loan/{loan_id}", headers=h_o)
    assert r.status_code == 200, "Owner should have access to the chat"
    
    # Borrower can access the chat
    h_b = {"Authorization": f"Bearer {borrower_token}"}
    r = c.get(f"/chat/loan/{loan_id}", headers=h_b)
    assert r.status_code == 200, "Borrower should have access to the chat"
