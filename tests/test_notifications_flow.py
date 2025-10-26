"""Pruebas de notificaciones integradas con el flujo actual"""
from fastapi.testclient import TestClient

from tests.helpers import register_user, login_user, auth_headers


def _setup_chat_notification(client: TestClient):
    """Crear usuarios, préstamo y generar una notificación de mensaje."""

    owner = register_user(client)
    borrower = register_user(client)

    owner_token = login_user(client, username=owner["username"])
    borrower_token = login_user(client, username=borrower["username"])

    # Crear libro del dueño
    book_resp = client.post(
        "/books/",
        json={
            "title": "Libro Notificaciones",
            "author": "Autor",
            "isbn": "9789876543217",
        },
        headers=auth_headers(owner_token),
    )
    assert book_resp.status_code == 201, book_resp.text
    book_id = book_resp.json()["id"]

    # Solicitar préstamo
    loan_resp = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower['id']}",
        headers=auth_headers(borrower_token),
    )
    assert loan_resp.status_code == 201, loan_resp.text
    loan_id = loan_resp.json()["loan_id"]

    # Aprobar préstamo
    approve_resp = client.post(
        f"/loans/{loan_id}/approve?lender_id={owner['id']}",
        headers=auth_headers(owner_token),
    )
    assert approve_resp.status_code == 200, approve_resp.text

    # Enviar mensaje para generar notificación
    message_resp = client.post(
        "/chat/send",
        json={"loan_id": loan_id, "content": "Hola, te escribo para coordinar la devolución."},
        headers=auth_headers(owner_token),
    )
    assert message_resp.status_code == 201, message_resp.text

    return {
        "owner": owner,
        "borrower": borrower,
        "owner_token": owner_token,
        "borrower_token": borrower_token,
        "loan_id": loan_id,
    }


def test_notification_created_after_chat_message(client: TestClient) -> None:
    """Enviar un mensaje debe generar notificación NEW_MESSAGE para el destinatario."""

    context = _setup_chat_notification(client)

    list_resp = client.get(
        "/notifications/",
        headers=auth_headers(context["borrower_token"]),
        params={"is_read": False},
    )
    assert list_resp.status_code == 200, list_resp.text
    notifications = list_resp.json()

    assert len(notifications) >= 1
    types = {n["type"] for n in notifications}
    assert "NEW_MESSAGE" in types


def test_notification_unread_count(client: TestClient) -> None:
    """El contador de no leídas refleja las notificaciones generadas."""

    context = _setup_chat_notification(client)

    count_resp = client.get(
        "/notifications/unread/count",
        headers=auth_headers(context["borrower_token"]),
    )
    assert count_resp.status_code == 200, count_resp.text
    initial = count_resp.json()["unread_count"]
    assert initial >= 1


def test_mark_all_notifications_as_read(client: TestClient) -> None:
    """Marcar todas como leídas retorna el número adecuado y limpia el contador."""

    context = _setup_chat_notification(client)

    mark_resp = client.post(
        "/notifications/read-all",
        headers=auth_headers(context["borrower_token"]),
    )
    assert mark_resp.status_code == 200, mark_resp.text
    marked = mark_resp.json()["marked_as_read"]
    assert marked >= 1

    count_resp = client.get(
        "/notifications/unread/count",
        headers=auth_headers(context["borrower_token"]),
    )
    assert count_resp.status_code == 200, count_resp.text
    assert count_resp.json()["unread_count"] == 0
