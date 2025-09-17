import uuid
import os
import pytest
from fastapi.testclient import TestClient

# Set environment variables before importing app
os.environ["TESTING"] = "true"
os.environ["DISABLE_RATE_LIMITING"] = "true"

from app.main import app


def test_register_login_me():
    c = TestClient(app)
    
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

    # Login with retry for rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        r = c.post(
            "/auth/login",
            data={"username": username, "password": "SuperSegura123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if r.status_code == 200:
            break
            
        if r.status_code == 429 and attempt < max_retries - 1:
            # Wait and retry
            time.sleep(1)
            continue
            
        assert r.status_code == 200, f"Login failed after {attempt + 1} attempts: {r.text}"
    
    # Verify login was successful
    assert r.status_code == 200, f"Login failed after {max_retries} attempts: {r.text}"
    token = r.json()["access_token"]
    assert token

    # /auth/me
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["username"] == username


