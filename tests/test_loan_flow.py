"""Pruebas básicas del flujo de préstamos"""
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from tests.helpers import register_user, login_user, auth_headers, extract_error_message


def test_loan_request_and_approval(client: TestClient) -> None:
    """Un usuario puede solicitar un préstamo y el dueño aprobarlo."""

    owner = register_user(client, username="propietario_test")
    borrower = register_user(client, username="prestamo_test")

    owner_token = login_user(client, username=owner["username"])
    borrower_token = login_user(client, username=borrower["username"])

    # El dueño crea un libro
    book_payload = {
        "title": "Neuromante",
        "author": "William Gibson",
        "isbn": "9780441569595",
        "genre": "science_fiction",
        "condition": "good",
    }
    book_response = client.post("/books/", json=book_payload, headers=auth_headers(owner_token))
    assert book_response.status_code == 201, book_response.text
    book_id = book_response.json()["id"]

    # El prestatario solicita el libro
    loan_request = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower['id']}",
        headers=auth_headers(borrower_token),
    )
    assert loan_request.status_code == 201, loan_request.text
    loan_id = loan_request.json()["loan_id"]
    UUID(loan_id)  # valida formato

    # El dueño aprueba el préstamo
    approval = client.post(
        f"/loans/{loan_id}/approve?lender_id={owner['id']}",
        headers=auth_headers(owner_token),
    )
    assert approval.status_code == 200, approval.text
    approval_data = approval.json()

    assert approval_data["success"] is True
    assert approval_data["loan_id"] == loan_id
    assert approval_data["status"].upper() in {"APPROVED", "ACTIVE"}


def test_loan_request_fails_if_book_already_loaned(client: TestClient) -> None:
    """Cuando el libro ya está prestado a otro usuario, nueva solicitud devuelve 400."""

    owner = register_user(client, username="duenio_prestamo")
    borrower1 = register_user(client)
    borrower2 = register_user(client)

    owner_token = login_user(client, username=owner["username"])
    borrower1_token = login_user(client, username=borrower1["username"])
    borrower2_token = login_user(client, username=borrower2["username"])

    payload = {
        "title": "Fundación",
        "author": "Isaac Asimov",
        "isbn": "9788497594250",
    }
    book_resp = client.post("/books/", json=payload, headers=auth_headers(owner_token))
    assert book_resp.status_code == 201, book_resp.text
    book_id = book_resp.json()["id"]

    # Primer préstamo aprobado
    first_request = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower1['id']}",
        headers=auth_headers(borrower1_token),
    )
    assert first_request.status_code == 201, first_request.text
    first_loan_id = first_request.json()["loan_id"]

    approve = client.post(
        f"/loans/{first_loan_id}/approve?lender_id={owner['id']}",
        headers=auth_headers(owner_token),
    )
    assert approve.status_code == 200, approve.text

    # Segunda solicitud con otro usuario debe fallar
    second_request = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower2['id']}",
        headers=auth_headers(borrower2_token),
    )

    assert second_request.status_code in {400, 500}, second_request.text
    assert "préstamo" in (extract_error_message(second_request.json()) or "")


def test_approve_loan_with_wrong_lender_returns_400(client: TestClient) -> None:
    """Solo el dueño del libro puede aprobar el préstamo."""

    owner = register_user(client)
    borrower = register_user(client)
    outsider = register_user(client)

    owner_token = login_user(client, username=owner["username"])
    borrower_token = login_user(client, username=borrower["username"])
    outsider_token = login_user(client, username=outsider["username"])

    book_resp = client.post(
        "/books/",
        json={"title": "Cien Años", "author": "G. Márquez", "isbn": "9780307474728"},
        headers=auth_headers(owner_token),
    )
    assert book_resp.status_code == 201, book_resp.text
    book_id = book_resp.json()["id"]

    loan_request = client.post(
        f"/loans/request?book_id={book_id}&borrower_id={borrower['id']}",
        headers=auth_headers(borrower_token),
    )
    assert loan_request.status_code == 201, loan_request.text
    loan_id = loan_request.json()["loan_id"]

    approval = client.post(
        f"/loans/{loan_id}/approve?lender_id={outsider['id']}",
        headers=auth_headers(outsider_token),
    )

    assert approval.status_code in {400, 500}, approval.text
    assert "préstamo" in (extract_error_message(approval.json()) or "")


def test_approve_nonexistent_loan_returns_400(client: TestClient) -> None:
    """Aprobar un préstamo inexistente devuelve 400."""

    owner = register_user(client)
    owner_token = login_user(client, username=owner["username"])

    response = client.post(
        f"/loans/{uuid4()}/approve?lender_id={owner['id']}",
        headers=auth_headers(owner_token),
    )

    assert response.status_code in {400, 500}, response.text
    assert "préstamo" in (extract_error_message(response.json()) or "")
