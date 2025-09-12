import uuid
from httpx import Client


def _register_and_login(client: Client):
    username = f"tok_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    user = r.json()
    r = client.post("/auth/login", data={"username": username, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = r.json()["access_token"]
    return user, token


def test_bearer_missing_or_malformed_returns_401(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    _user, token = _register_and_login(c)
    # Sin header
    r = c.get("/auth/me")
    assert r.status_code == 401
    # Header mal formado
    r = c.get("/auth/me", headers={"Authorization": "Bearer"})
    assert r.status_code == 401
    # Token inválido
    r = c.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert r.status_code == 401

