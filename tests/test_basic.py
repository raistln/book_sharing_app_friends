from httpx import Client


def test_root_and_health(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    r = c.get("/")
    assert r.status_code == 200
    assert "message" in r.json()

    r = c.get("/health")
    assert r.status_code == 200

