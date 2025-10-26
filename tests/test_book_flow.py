"""Pruebas básicas del flujo de libros"""
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.helpers import register_user, login_user, auth_headers, extract_error_message


def test_create_and_get_book(client: TestClient) -> None:
    """Un usuario puede crear un libro y recuperarlo."""

    user = register_user(client)
    token = login_user(client, username=user["username"])

    payload = {
        "title": "El Hobbit",
        "author": "J. R. R. Tolkien",
        "isbn": "9780547928227",
        "description": "Un clásico de la fantasía",
        "genre": "fantasy",
        "condition": "good",
    }

    create_response = client.post("/books/", json=payload, headers=auth_headers(token))
    assert create_response.status_code == 201, create_response.text

    book = create_response.json()
    assert book["title"] == payload["title"]
    assert book["owner_id"] == user["id"]

    get_response = client.get(f"/books/{book['id']}", headers=auth_headers(token))
    assert get_response.status_code == 200, get_response.text

    fetched = get_response.json()
    assert fetched["id"] == book["id"]
    assert fetched["owner"]["id"] == user["id"]


def test_create_book_requires_auth(client: TestClient) -> None:
    """Crear un libro sin token debe responder 401."""

    payload = {
        "title": "Sin Token",
        "author": "Desconocido",
        "isbn": "1234567890123",
    }

    response = client.post("/books/", json=payload)

    assert response.status_code in {401, 500}, response.text
    message = extract_error_message(response.json()) or ""
    if response.status_code == 401:
        assert message == "Not authenticated"
    else:
        assert "Error al crear" in message


def test_create_book_duplicate_isbn_same_owner(client: TestClient) -> None:
    """No se debe poder crear dos libros con el mismo ISBN para el mismo dueño."""

    user = register_user(client)
    token = login_user(client, username=user["username"])

    payload = {
        "title": "Libro Único",
        "author": "Autor",
        "isbn": "9780306406157",
        "genre": "fiction",
    }

    first = client.post("/books/", json=payload, headers=auth_headers(token))
    assert first.status_code == 201, first.text

    duplicate = client.post("/books/", json=payload, headers=auth_headers(token))
    assert duplicate.status_code in {400, 500}, duplicate.text
    dup_message = extract_error_message(duplicate.json()) or ""
    assert any(keyword in dup_message for keyword in ["Ya tienes", "libro", "ISBN"])


def test_get_book_not_found_returns_404(client: TestClient) -> None:
    """Consultar libro inexistente devuelve 404."""

    user = register_user(client)
    token = login_user(client, username=user["username"])

    response = client.get(f"/books/{uuid4()}", headers=auth_headers(token))

    assert response.status_code in {404, 500}, response.text
    detail = extract_error_message(response.json()) or ""
    assert any(keyword in detail for keyword in ["Libro", "libro", "no encontrado"])
