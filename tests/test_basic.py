from fastapi.testclient import TestClient
from app.main import app


def test_root_and_health():
    c = TestClient(app)
    
    # Test root endpoint
    r = c.get("/")
    assert r.status_code == 200, "Root endpoint should return 200"
    assert "message" in r.json(), "Root response should contain 'message' field"
    
    # Test health check endpoint
    r = c.get("/health")
    assert r.status_code == 200, "Health check endpoint should return 200"
    health_data = r.json()
    assert "status" in health_data, "Health check should contain 'status' field"
    assert health_data["status"] == "healthy", "Health status should be 'healthy'"

