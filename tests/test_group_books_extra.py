import uuid
from httpx import Client


def _register_and_login(client: Client):
    username = f"gbx_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    user = r.json()
    r = client.post("/auth/login", data={"username": username, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = r.json()["access_token"]
    return user, token


def _create_group(client: Client, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post("/groups/", json={"name": "G", "description": "D"}, headers=headers)
    return r.json()


def _create_book(client: Client, owner, token, **extra):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": "T", "author": "A", "isbn": "1", "description": "d", "owner_id": owner["id"]}
    payload.update(extra)
    r = client.post("/books/", json=payload, headers=headers)
    return r.json()


def test_filters_combinations_and_pagination_edges(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    g = _create_group(c, token)
    gid = g["id"]
    # Crear libros con combinaciones
    _create_book(c, user, token, book_type="novel", genre="science_fiction")
    _create_book(c, user, token, book_type="comic", genre="fiction")
    _create_book(c, user, token, book_type="novel", genre="fiction")
    # Filtro combinado
    r = c.get(f"/groups/{gid}/books?book_type=novel&genre=science_fiction&limit=1&offset=0", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    # Offset grande
    r = c.get(f"/groups/{gid}/books?limit=1&offset=1000", headers=headers)
    assert r.status_code == 200
    assert r.json() == []

