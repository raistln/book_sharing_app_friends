"""Pruebas básicas de autenticación con el flujo actual"""
from fastapi.testclient import TestClient

from tests.helpers import register_user, login_user, auth_headers, extract_error_message


def test_register_login_and_me(client: TestClient) -> None:
    """Registrar un usuario, iniciar sesión y recuperar su perfil."""

    user = register_user(client)
    token = login_user(client, username=user["username"])

    response = client.get("/users/me", headers=auth_headers(token))

    assert response.status_code == 200, response.text
    profile = response.json()

    assert profile["id"] == user["id"]
    assert profile["username"] == user["username"]
    assert profile["email"].lower() == user["email"].lower()
    assert profile["is_active"] is True


def test_login_with_invalid_credentials(client: TestClient) -> None:
    """Login con credenciales incorrectas debe responder 401."""

    user = register_user(client)

    response = client.post(
        "/auth/login",
        json={"username": user["username"], "password": "ContraseñaErrónea123"},
    )

    assert response.status_code == 401, response.text
    body = response.json()
    assert extract_error_message(body) == "Credenciales inválidas"


def test_login_with_missing_fields(client: TestClient) -> None:
    """Login sin password debe responder 422."""

    register_user(client)

    response = client.post(
        "/auth/login",
        json={"username": "usuario_sin_password"},
    )

    assert response.status_code == 422, response.text
    body = response.json()
    assert extract_error_message(body) == "Usuario y contraseña requeridos"


def test_me_requires_token(client: TestClient) -> None:
    """Acceder a /users/me sin token debe devolver 401."""

    response = client.get("/users/me")

    assert response.status_code == 401, response.text
    body = response.json()
    assert extract_error_message(body) == "Not authenticated"
