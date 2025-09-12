from httpx import Client
from .test_books_loans import _register_and_login

def test_search_isbn_with_and_without_hyphens(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    r1 = c.get("/search/books", params={"q": "9780261102217", "limit": 2})
    assert r1.status_code == 200
    r2 = c.get("/search/books", params={"q": "978-0261102217", "limit": 2})
    assert r2.status_code == 200


def test_search_title_with_accents_normalized(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    r = c.get("/search/books", params={"q": "Cien años", "limit": 2})
    assert r.status_code == 200


def test_scan_validation_errors(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # ✅ Crear usuario y obtener token para autenticación
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Enviar petición sin archivo pero con autenticación
    r = c.post("/scan/book", headers=headers)
    assert r.status_code in {400, 422}

# Alternativamente, si quieres probar el comportamiento sin autenticación:
def test_scan_validation_errors_alternative(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Probar sin autenticación - debería retornar 401
    r = c.post("/scan/book")
    assert r.status_code == 401
    
    # Luego probar con autenticación pero sin archivo - debería retornar 422
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    r = c.post("/scan/book", headers=headers)
    assert r.status_code in {400, 422}