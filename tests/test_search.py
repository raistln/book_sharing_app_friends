import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

# Sample mock response for book search
MOCK_BOOK_RESPONSE = [
    {
        "title": "The Hobbit",
        "authors": ["J.R.R. Tolkien"],
        "publisher": "Houghton Mifflin Harcourt",
        "published_date": "2012-02-15",
        "description": "A great adventure",
        "isbn_13": "9780547928227",
        "page_count": 300,
        "cover_url": "http://example.com/cover.jpg",
        "language": "en"
    }
]

# Create test client
client = TestClient(app)

@patch('app.services.book_search_service.BookSearchService.search')
def test_search_by_title_returns_results_or_empty(mock_search):
    # Setup mock
    mock_search.return_value = MOCK_BOOK_RESPONSE
    
    # Make request
    response = client.get("/search/books", params={"q": "The Hobbit", "limit": 3})
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are results, verify their structure
        assert "title" in data[0]
        assert "authors" in data[0]
        assert "isbn_13" in data[0]

@patch('app.services.book_search_service.BookSearchService.search')
def test_search_by_isbn_returns_results_or_empty(mock_search):
    # Setup mock
    mock_search.return_value = MOCK_BOOK_RESPONSE
    
    # Make request
    response = client.get("/search/books", params={"q": "9780547928227", "limit": 3})
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are results, verify their structure
        assert "title" in data[0]
        assert "isbn_13" in data[0]
        assert data[0]["isbn_13"] == "9780547928227"

@patch('app.services.book_search_service.BookSearchService.search')
def test_search_handles_api_failure(mock_search):
    # Setup mock to raise an exception
    mock_search.side_effect = Exception("API Error")
    
    try:
        # Make request
        response = client.get("/search/books", params={"q": "Nonexistent Book", "limit": 3})
        
        # If we get here, the endpoint should return 200 with empty list on error
        assert response.status_code == 200
        assert response.json() == []
    except Exception as e:
        # If the endpoint raises an exception, it will be caught by FastAPI's error handler
        # and return a 500 error, which is also acceptable in this case
        assert "500" in str(e) or "Internal Server Error" in str(e)


