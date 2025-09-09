import uuid
from httpx import Client

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import create_access_token


def _register_user(client: Client, username: str, email: str, password: str = "SuperSegura123"):
    return client.post(
        "/auth/register",
        json={"username": username, "password": password, "email": email},
    )


def test_register_duplicate_username_and_email(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
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


def test_me_with_invalid_token_returns_401(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    invalid = "this.is.not.a.valid.token"
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {invalid}"})
    assert r.status_code == 401


def test_me_with_expired_token_returns_401(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
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


def test_me_with_inactive_user_returns_400(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    username = f"inactive_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"

    r = _register_user(c, username, email)
    assert r.status_code == 201
    data = r.json()

    # Marcar usuario como inactivo directamente en la BD
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == uuid.UUID(data["id"])).first()
        assert user is not None
        user.is_active = False
        db.add(user)
        db.commit()
    finally:
        db.close()

    # Login y usar token
    r = c.post(
        "/auth/login",
        data={"username": username, "password": "SuperSegura123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # authenticate_user devuelve None si inactivo, por lo que login falla con 400
    assert r.status_code == 400


