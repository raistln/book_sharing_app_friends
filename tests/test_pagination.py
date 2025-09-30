"""Tests for pagination utility."""
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.pagination import (
    PaginationParams, 
    PaginatedResponse,
    paginate_query, 
    paginate_list,
    create_pagination_metadata
)

# Test models - Using SQLAlchemy 2.0 style
Base = declarative_base()

# Add __allow_unmapped__ to suppress PytestCollectionWarning
class TestModel(Base):
    __tablename__ = 'test_models'
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    # Add test data
    for i in range(1, 101):
        db.add(TestModel(id=i, name=f"Item {i}"))
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestPaginationParams:
    def test_pagination_params_defaults(self):
        """Test PaginationParams with default values."""
        params = PaginationParams()
        assert params.page == 1
        assert params.per_page == 20
        
    def test_pagination_params_custom_values(self):
        """Test PaginationParams with custom values."""
        params = PaginationParams(page=2, per_page=10)
        assert params.page == 2
        assert params.per_page == 10
        
    def test_pagination_params_validation(self):
        """Test PaginationParams validation."""
        # The actual implementation clamps values in __post_init__
        params = PaginationParams(page=0)
        assert params.page == 1  # Should be clamped to min 1
        
        params = PaginationParams(per_page=0)
        assert params.per_page == 1  # Should be clamped to min 1
        
        params = PaginationParams(per_page=101)
        assert params.per_page == 100  # Should be clamped to max 100

class TestPaginateQuery:
    def test_paginate_query_defaults(self, db_session):
        """Test paginate_query with default parameters."""
        query = db_session.query(TestModel)
        result = paginate_query(query)
        
        assert len(result.items) == 20  # Default per_page
        assert result.page == 1
        assert result.per_page == 20
        assert result.total == 100
        assert result.total_pages == 5  # 100/20 = 5 pages
        
    def test_paginate_query_custom_page(self, db_session):
        """Test paginate_query with custom page and per_page."""
        query = db_session.query(TestModel)
        result = paginate_query(query, page=2, per_page=10)
        
        assert len(result.items) == 10
        assert result.page == 2
        assert result.per_page == 10
        assert result.total == 100
        assert result.total_pages == 10  # 100/10 = 10 pages
        assert result.items[0].id == 11  # First item on page 2 (items 11-20)
        
    def test_paginate_query_out_of_range(self, db_session):
        """Test paginate_query with out of range page."""
        query = db_session.query(TestModel)
        result = paginate_query(query, page=100, per_page=10)
        
        # Should return empty list for pages beyond the data
        assert len(result.items) == 0
        assert result.page == 100
        assert result.total == 100
        
    def test_paginate_query_empty_result(self, db_session):
        """Test paginate_query with no results."""
        query = db_session.query(TestModel).filter(TestModel.id < 0)  # No matches
        result = paginate_query(query, page=1, per_page=10)
        assert result.total == 0
        assert result.total_pages == 1  # Even with no items, we have 1 page
        assert result.has_next is False
        assert result.has_prev is False
        assert result.next_page is None
        assert result.prev_page is None

class TestPaginateList:
    def test_paginate_list_defaults(self):
        """Test paginate_list with default parameters."""
        items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
        result = paginate_list(items)
        
        assert len(result.items) == 20
        assert result.page == 1
        assert result.per_page == 20
        assert result.total == 100
        assert result.total_pages == 5
        assert result.has_next is True
        assert result.next_page == 2
        assert result.has_prev is False
        assert result.prev_page is None
        
    def test_paginate_list_custom_page(self):
        """Test paginate_list with custom page and per_page."""
        items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
        result = paginate_list(items, page=2, per_page=10)
        
        assert len(result.items) == 10
        assert result.page == 2
        assert result.per_page == 10
        assert result.total == 100
        assert result.total_pages == 10
        assert result.items[0]["id"] == 11
        assert result.has_next is True
        assert result.next_page == 3
        assert result.has_prev is True
        assert result.prev_page == 1
        
    def test_paginate_list_empty(self):
        """Test paginate_list with empty list."""
        result = paginate_list([], page=1, per_page=10)
        
        assert len(result.items) == 0
        assert result.total == 0
        assert result.total_pages == 1  # Even with no items, we have 1 page
        assert result.has_next is False
        assert result.has_prev is False
        assert result.next_page is None
        assert result.prev_page is None


class TestCreatePaginationMetadata:
    def test_create_pagination_metadata(self):
        """Test create_pagination_metadata function."""
        metadata = create_pagination_metadata(total=100, page=2, per_page=10)
        
        assert metadata["total"] == 100
        assert metadata["page"] == 2
        assert metadata["per_page"] == 10
        assert metadata["total_pages"] == 10
        assert metadata["has_next"] is True
        assert metadata["has_prev"] is True
        assert metadata["next_page"] == 3
        assert metadata["prev_page"] == 1
        
    def test_create_pagination_metadata_first_page(self):
        """Test pagination metadata for first page."""
        metadata = create_pagination_metadata(total=100, page=1, per_page=10)
        
        assert metadata["has_prev"] is False
        assert metadata["prev_page"] is None
        assert metadata["next_page"] == 2
        
    def test_create_pagination_metadata_last_page(self):
        """Test pagination metadata for last page."""
        metadata = create_pagination_metadata(total=100, page=10, per_page=10)
        
        assert metadata["has_next"] is False
        assert metadata["next_page"] is None
        assert metadata["prev_page"] == 9
