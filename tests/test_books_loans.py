import uuid
from httpx import Client


def _register_and_login(client: Client):
    username = f"bkl_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"

    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    assert r.status_code == 201, r.text
    user = r.json()

    r = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return user, token


def test_books_crud_and_loan_flow(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)

    # Usuario owner
    owner, owner_token = _register_and_login(c)
    # Usuario borrower
    borrower, borrower_token = _register_and_login(c)

    # Crear libro como owner
    book_payload = {
        "title": "El Quijote",
        "author": "Cervantes",
        "isbn": "9788491050290",
        "description": "Clásico",
        "owner_id": owner["id"],
    }
    r = c.post("/books/", json=book_payload)
    assert r.status_code == 201, r.text
    book = r.json()
    assert book["owner_id"] == owner["id"]
    assert book["status"] == "available"

    # Listado
    r = c.get("/books/")
    assert r.status_code == 200
    assert any(b["id"] == book["id"] for b in r.json())

    # Prestar libro al borrower
    r = c.post(
        "/loans/loan",
        params={"book_id": book["id"], "borrower_id": borrower["id"]},
    )
    assert r.status_code == 200, r.text

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


