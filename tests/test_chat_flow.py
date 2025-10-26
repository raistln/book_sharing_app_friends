"""Pruebas del módulo de chat"""
from time import sleep
from uuid import UUID

from fastapi.testclient import TestClient

from tests.helpers import register_user, login_user, auth_headers, extract_error_message


def _setup_loan(client: TestClient):
    """Crear dos usuarios, libro y préstamo aprobado para utilizar el chat."""

    owner = register_user(client)
    borrower = register_user(client)

    owner_token = login_user(client, username=owner["username"])
    borrower_token = login_user(client, username=borrower["username"])

    book_resp = client.post(
        "/books/",
        json={
            "title": "Chat Test",
            "author": "Autor",
            "isbn": "9781234567897",
        },
        headers=auth_headers(owner_token),
    )
    assert book_resp.status_code == 201, book_resp.text
    book_id = book_resp.json()["id"]

    loan_resp = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower['id']}",
        headers=auth_headers(borrower_token),
    )
    assert loan_resp.status_code == 201, loan_resp.text
    loan_id = loan_resp.json()["loan_id"]
    UUID(loan_id)

    approve_resp = client.post(
        f"/loans/{loan_id}/approve?lender_id={owner['id']}",
        headers=auth_headers(owner_token),
    )
    assert approve_resp.status_code == 200, approve_resp.text

    return owner, borrower, owner_token, borrower_token, loan_id


def test_chat_send_and_receive_messages(client: TestClient) -> None:
    """Enviar un mensaje y recuperarlo."""

    owner, borrower, owner_token, borrower_token, loan_id = _setup_loan(client)

    send_resp = client.post(
        "/chat/send",
        json={"loan_id": loan_id, "content": "Hola, ¿cómo va todo?"},
        headers=auth_headers(owner_token),
    )
    assert send_resp.status_code == 201, send_resp.text
    message = send_resp.json()
    assert message["loan_id"] == loan_id
    assert message["sender_id"] == owner["id"]

    list_resp = client.get(
        f"/chat/loan/{loan_id}",
        headers=auth_headers(borrower_token),
    )
    assert list_resp.status_code == 200, list_resp.text
    messages = list_resp.json()
    assert len(messages) >= 1
    assert any(msg["content"] == "Hola, ¿cómo va todo?" for msg in messages)


def test_chat_polling_since_returns_only_new_messages(client: TestClient) -> None:
    """El parámetro since devuelve solo mensajes nuevos."""

    owner, borrower, owner_token, borrower_token, loan_id = _setup_loan(client)

    first = client.post(
        "/chat/send",
        json={"loan_id": loan_id, "content": "Mensaje 1"},
        headers=auth_headers(owner_token),
    )
    assert first.status_code == 201, first.text

    sleep(1.1)
    second = client.post(
        "/chat/send",
        json={"loan_id": loan_id, "content": "Mensaje 2"},
        headers=auth_headers(borrower_token),
    )
    assert second.status_code == 201, second.text
    second_data = second.json()

    polling_resp = client.get(
        f"/chat/loan/{loan_id}",
        params={"since": first.json()["created_at"]},
        headers=auth_headers(owner_token),
    )
    assert polling_resp.status_code == 200, polling_resp.text
    messages = polling_resp.json()
    assert any(msg["id"] == second_data["id"] for msg in messages)


def test_chat_access_control(client: TestClient) -> None:
    """Un tercero no puede leer el chat de un préstamo ajeno."""

    owner, borrower, owner_token, borrower_token, loan_id = _setup_loan(client)
    stranger = register_user(client)
    stranger_token = login_user(client, username=stranger["username"])

    resp = client.get(
        f"/chat/loan/{loan_id}",
        headers=auth_headers(stranger_token),
    )
    assert resp.status_code == 403, resp.text
    msg = extract_error_message(resp.json()) or ""
    msg = msg.lower() if isinstance(msg, str) else str(msg).lower()
    assert "forbidden" in msg
