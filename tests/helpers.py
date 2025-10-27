"""Utilidades compartidas para los tests de integración"""
from __future__ import annotations

import uuid
from typing import Dict, Any

from fastapi.testclient import TestClient


DEFAULT_PASSWORD = "TestPassw0rd!"


def register_user(
    client: TestClient,
    *,
    username: str | None = None,
    password: str = DEFAULT_PASSWORD,
    email: str | None = None,
    full_name: str = "Usuario de Prueba",
) -> Dict[str, str]:
    """Registrar un usuario de prueba mediante el endpoint /auth/register."""

    username = username or f"user_{uuid.uuid4().hex[:8]}"
    email = email or f"{username}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )

    assert response.status_code == 201, f"Fallo al registrar usuario: {response.text}"
    return response.json()


def register_user_raw(
    client: TestClient,
    payload: Dict[str, str] | None = None,
):
    """Registrar usuario sin validaciones helper (devuelve response)."""

    payload = payload or {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "password": DEFAULT_PASSWORD,
    }

    return client.post("/auth/register", json=payload)


def extract_error_message(data: Dict[str, Any]) -> str | None:
    """Obtener mensaje de error desde distintas estructuras de respuesta."""

    detail = data.get("detail")
    if isinstance(detail, dict):
        return detail.get("msg") or detail.get("message") or detail.get("detail")
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict):
            return first.get("msg") or first.get("message")
        if isinstance(first, str):
            return first
    if isinstance(detail, str):
        return detail

    return data.get("message")


def login_user(
    client: TestClient,
    *,
    username: str,
    password: str = DEFAULT_PASSWORD,
) -> str:
    """Iniciar sesión y devolver el token de acceso."""

    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 200, f"Fallo al iniciar sesión: {response.text}"
    data = response.json()
    assert "access_token" in data, f"Respuesta sin token: {data}"
    return data["access_token"]


def auth_headers(token: str) -> Dict[str, str]:
    """Construir los headers con autenticación Bearer."""

    return {"Authorization": f"Bearer {token}"}
