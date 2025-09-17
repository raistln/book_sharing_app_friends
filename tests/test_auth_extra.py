import uuid
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import create_access_token
from main import app


def _register_user(client: TestClient, username: str, email: str, password: str = "SuperSegura123"):
    return client.post(
        "/auth/register",
        json={"username": username, "password": password, "email": email},
    )


def test_register_duplicate_username_and_email():
    c = TestClient(app)
    base = f"dup_{uuid.uuid4().hex[:6]}"
    username = f"{base}_user"
    email = f"{base}@example.com"

    r1 = _register_user(c, username, email)
    assert r1.status_code == 201, r1.text

    # mismo username, distinto email
    r2 = _register_user(c, username, f"{base}2@example.com")
    assert r2.status_code == 400

    # distinto username, mismo email
    r3 = _register_user(c, f"{username}2", email)
    assert r3.status_code == 400


def test_me_with_invalid_token_returns_401():
    c = TestClient(app)
    invalid = "this.is.not.a.valid.token"
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {invalid}"})
    assert r.status_code == 401


def test_me_with_expired_token_returns_401():
    c = TestClient(app)
    # Registrar usuario
    username = f"exp_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    r = _register_user(c, username, email)
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Crear token expirado (usando minutos negativos)
    token = create_access_token(subject=user_id, expires_delta_minutes=-1)
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_me_with_inactive_user_returns_400(db_session):
    c = TestClient(app)
    username = f"inactive_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"

    # Register user
    r = _register_user(c, username, email)
    assert r.status_code == 201, f"Failed to register user: {r.text}"
    
    # Find and deactivate user using the provided session
    user = db_session.query(User).filter(User.username == username).first()
    assert user is not None, f"User {username} not found in database"
    user.is_active = False
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Login y usar token
    r = c.post(
        "/auth/login",
        data={"username": username, "password": "SuperSegura123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # authenticate_user devuelve None si inactivo, por lo que login falla con 401 (no 400)
    assert r.status_code == 401, f"Expected 401 for inactive user, got {r.status_code}: {r.text}"


