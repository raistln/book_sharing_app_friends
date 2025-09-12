import uuid
from httpx import Client


def _register_and_login(client: Client):
    username = f"loan_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    assert r.status_code == 201
    user = r.json()
    r = client.post("/auth/login", data={"username": username, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = r.json()["access_token"]
    return user, token


def _create_book(client: Client, owner, token, title="T"):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title, "author": "A", "isbn": "1", "description": "d", "owner_id": owner["id"]}
    r = client.post("/books/", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_double_loan_concurrent_returns_400(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    owner, owner_token = _register_and_login(c)
    b1, t1 = _register_and_login(c)
    b2, t2 = _register_and_login(c)
    book = _create_book(c, owner, owner_token)
    # Primer préstamo OK
    r = c.post("/loans/loan", params={"book_id": book["id"], "borrower_id": b1["id"]})
    assert r.status_code == 200, r.text
    # Segundo préstamo concurrente debe fallar 400
    r = c.post("/loans/loan", params={"book_id": book["id"], "borrower_id": b2["id"]})
    assert r.status_code == 400, r.text


def test_return_book_not_loaned_returns_400(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    owner, owner_token = _register_and_login(c)
    book = _create_book(c, owner, owner_token)
    # Devolver sin estar prestado
    r = c.post("/loans/return", params={"book_id": book["id"]})
    assert r.status_code == 400, r.text

