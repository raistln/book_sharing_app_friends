import random
from httpx import Client


def _register_and_login(c: Client):
    u = f"user_{random.randint(100000,999999)}"
    email = f"{u}@example.com"
    r = c.post("/auth/register", json={"username": u, "email": email, "password": "Passw0rd!"})
    assert r.status_code == 201
    r = c.post("/auth/token", data={"username": u, "password": "Passw0rd!"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    me = c.get("/users/me", headers=h).json()
    return me, token


def _create_book(c: Client, owner_token: str, title="T", author="A"):
    h = {"Authorization": f"Bearer {owner_token}"}
    r = c.post("/books/", json={"title": title, "author": author}, headers=h)
    assert r.status_code == 201
    return r.json()


def _loan_book(c: Client, book_id: str, borrower_id: str):
    return c.post("/loans/loan", params={"book_id": book_id, "borrower_id": borrower_id})


def test_chat_send_and_receive(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    owner, owner_token = _register_and_login(c)
    borrower, borrower_token = _register_and_login(c)

    book = _create_book(c, owner_token, "ChatBook", "Autor")

    r = _loan_book(c, book["id"], borrower["id"])  # préstamo inmediato
    assert r.status_code == 201
    loan_id = r.json()["loan_id"]

    # borrower envía mensaje
    h_b = {"Authorization": f"Bearer {borrower_token}"}
    r = c.post("/chat/send", json={"loan_id": loan_id, "content": "Hola"}, headers=h_b)
    assert r.status_code == 201

    # owner lee mensajes
    h_o = {"Authorization": f"Bearer {owner_token}"}
    r = c.get(f"/chat/loan/{loan_id}", headers=h_o)
    assert r.status_code == 200
    msgs = r.json()
    assert len(msgs) >= 1
    assert msgs[0]["content"] == "Hola"


def test_chat_access_control(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    owner, owner_token = _register_and_login(c)
    borrower, borrower_token = _register_and_login(c)
    intruder, intr_token = _register_and_login(c)

    book = _create_book(c, owner_token, "ChatBook2", "Autor")
    r = _loan_book(c, book["id"], borrower["id"])  # préstamo
    assert r.status_code == 201
    loan_id = r.json()["loan_id"]

    # Intruso intenta enviar/leer
    h_i = {"Authorization": f"Bearer {intr_token}"}
    r = c.post("/chat/send", json={"loan_id": loan_id, "content": "spy"}, headers=h_i)
    assert r.status_code == 403
    r = c.get(f"/chat/loan/{loan_id}", headers=h_i)
    assert r.status_code == 403
