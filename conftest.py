"""
Test configuration and fixtures
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set environment variables before importing app to ensure rate limiting is disabled
os.environ["TESTING"] = "true"
os.environ["DISABLE_RATE_LIMITING"] = "true"

from app.database import get_db, Base
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with disabled rate limiting"""
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup
    try:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()  # Close all connections
        if os.path.exists("./test.db"):
            import time
            time.sleep(0.1)  # Brief wait for file handles to close
            os.remove("./test.db")
    except (PermissionError, OSError):
        # File might be locked, ignore cleanup error
        pass

@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    """Database session fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def clean_db():
    """Clean database before each test"""
    # Clear all tables
    db = TestingSessionLocal()
    try:
        from sqlalchemy import text
        # Get all table names
        tables = Base.metadata.tables.keys()
        for table in tables:
            db.execute(text(f"DELETE FROM {table}"))
        db.commit()
    finally:
        db.close()
