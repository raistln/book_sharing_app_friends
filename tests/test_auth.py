import uuid
from httpx import Client


def test_register_login_me(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)

    # Registrar usuario único
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "SuperSegura123",
        "email": f"{username}@example.com",
    }
    r = c.post("/auth/register", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["username"] == username
    assert data["is_active"] is True

    # Login
    r = c.post(
        "/auth/login",
        data={"username": username, "password": "SuperSegura123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token

    # /auth/me
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["username"] == username


