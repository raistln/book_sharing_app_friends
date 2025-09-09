from httpx import Client


def test_search_by_title_returns_results_or_empty(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    r = c.get("/search/books", params={"q": "The Hobbit", "limit": 3})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Puede ser vacío si la API externa falla o rate-limita; no forzamos contenido


def test_search_by_isbn_returns_results_or_empty(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    r = c.get("/search/books", params={"q": "9780261102217", "limit": 3})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


