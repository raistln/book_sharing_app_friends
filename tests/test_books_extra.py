import uuid
from httpx import Client
from test_books_loans import _register_and_login  # o desde donde esté definida

def _register_and_login(client: Client):
    username = f"bkx_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    user = r.json()
    r = client.post("/auth/login", data={"username": username, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = r.json()["access_token"]
    return user, token


def test_update_status_invalid_returns_400(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "title": "T", 
        "author": "A", 
        "isbn": "1", 
        "description": "d", 
        "owner_id": user["id"]
    }
    r = c.post("/books/", json=payload, headers=headers)
    assert r.status_code == 201
    book = r.json()
    
    # ✅ Incluir headers y esperar 422 (error de validación Pydantic)
    r = c.put(f"/books/{book['id']}", json={"status": "invalid_state"}, headers=headers)
    assert r.status_code == 422
