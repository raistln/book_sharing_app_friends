import uuid
from fastapi.testclient import TestClient
from app.main import app


def _register_and_login(client: TestClient):
    username = f"tok_{uuid.uuid4().hex[:8]}"
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
    assert r.status_code == 200, f"Failed to login: {r.text}"
    token = r.json()["access_token"]
    
    return user, token


def test_bearer_missing_or_malformed_returns_401():
    c = TestClient(app)
    _user, _token = _register_and_login(c)
    
    # Test missing header
    r = c.get("/auth/me")
    assert r.status_code == 401, "Should require authentication"
    
    # Test malformed header (no token)
    r = c.get("/auth/me", headers={"Authorization": "Bearer"})
    assert r.status_code == 401, "Should reject malformed Bearer token"
    
    # Test invalid token
    r = c.get("/auth/me", headers={"Authorization": "Bearer invalid_token_123"})
    assert r.status_code == 401, "Should reject invalid token"

