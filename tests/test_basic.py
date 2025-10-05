from fastapi.testclient import TestClient
from app.main import app

def test_root_and_health(client):
    """Test root endpoint and health check"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Bienvenido" in data["message"]
    assert "version" in data
    assert data["version"] == "0.1.0"

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    assert "status" in health_data
    assert health_data["status"] == "healthy", "Health status should be 'healthy'"
