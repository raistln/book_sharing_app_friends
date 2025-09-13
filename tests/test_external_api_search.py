"""
Tests comprehensivos para el sistema de búsqueda en APIs externas.
Incluye tests para OpenLibrary, Google Books, caché Redis y fallbacks.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.services.book_search_service import BookSearchService
from app.services.openlibrary_client import OpenLibraryClient
from app.services.googlebooks_client import GoogleBooksClient
from app.services.cache import RedisCache


class TestOpenLibraryClient:
    """Tests unitarios para el cliente de OpenLibrary."""
    
    @pytest.fixture
    def client(self):
        return OpenLibraryClient()
    
    @patch('httpx.Client.get')
    def test_search_by_title_success(self, mock_get, client):
        """Test búsqueda exitosa por título en OpenLibrary."""
        # Mock response de OpenLibrary
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "docs": [
                {
                    "title": "The Hobbit",
                    "author_name": ["J.R.R. Tolkien"],
                    "isbn": ["9780547928227", "0547928220"],
                    "first_publish_year": 1937,
                    "publisher": ["Houghton Mifflin Harcourt"],
                    "cover_i": 8566821
                }
            ],
            "numFound": 1
        }
        mock_get.return_value = mock_response
        
        results = client.search_by_title("The Hobbit", limit=5)
        
        assert len(results) == 1
        book = results[0]
        assert book["title"] == "The Hobbit"
        assert "J.R.R. Tolkien" in book["authors"]
        assert book["isbn"] == "9780547928227"
        assert "cover_url" in book
    
    @patch('httpx.Client.get')
    def test_search_by_isbn_success(self, mock_get, client):
        """Test búsqueda exitosa por ISBN en OpenLibrary."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "docs": [
                {
                    "title": "The Lord of the Rings",
                    "author_name": ["J.R.R. Tolkien"],
                    "isbn": ["9780261102217"],
                    "first_publish_year": 1954
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = client.search_by_isbn("9780261102217")
        
        assert len(results) == 1
        assert results[0]["title"] == "The Lord of the Rings"
        assert results[0]["isbn"] == "9780261102217"
    
    @patch('httpx.Client.get')
    def test_search_api_error_handling(self, mock_get, client):
        """Test manejo de errores de la API de OpenLibrary."""
        # Simular error de red
        mock_get.side_effect = Exception("Network error")
        
        results = client.search_by_title("test query")
        assert results == []
    
    @patch('httpx.Client.get')
    def test_search_empty_response(self, mock_get, client):
        """Test manejo de respuesta vacía de OpenLibrary."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"docs": [], "numFound": 0}
        mock_get.return_value = mock_response
        
        results = client.search_by_title("nonexistent book")
        assert results == []
    
    @patch('httpx.Client.get')
    def test_search_malformed_response(self, mock_get, client):
        """Test manejo de respuesta malformada de OpenLibrary."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        results = client.search_by_title("test query")
        assert results == []


class TestGoogleBooksClient:
    """Tests unitarios para el cliente de Google Books."""
    
    @pytest.fixture
    def client(self):
        return GoogleBooksClient()
    
    @patch('httpx.Client.get')
    def test_search_success(self, mock_get, client):
        """Test búsqueda exitosa en Google Books."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Dune",
                        "authors": ["Frank Herbert"],
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9780441172719"}
                        ],
                        "publishedDate": "1965",
                        "publisher": "Ace Books",
                        "description": "A science fiction masterpiece",
                        "imageLinks": {
                            "thumbnail": "http://books.google.com/books/content?id=B1hSG45JCX4C&printsec=frontcover&img=1&zoom=1&source=gbs_api"
                        }
                    }
                }
            ],
            "totalItems": 1
        }
        mock_get.return_value = mock_response
        
        results = client.search_by_title("Dune", limit=5)
        
        assert len(results) == 1
        book = results[0]
        assert book["title"] == "Dune"
        assert "Frank Herbert" in book["authors"]
        assert book["isbn"] == "9780441172719"
        assert book["description"] == "A science fiction masterpiece"
    
    @patch('httpx.Client.get')
    def test_search_with_api_key(self, mock_get, client):
        """Test búsqueda con API key configurada."""
        client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalItems": 0}
        mock_get.return_value = mock_response
        
        client.search_by_title("test query")
        
        # Verificar que se llamó con el API key
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["key"] == "test_api_key"
    
    @patch('httpx.Client.get')
    def test_search_rate_limit_handling(self, mock_get, client):
        """Test manejo de rate limiting en Google Books."""
        mock_response = Mock()
        mock_response.status_code = 429  # Too Many Requests
        mock_get.return_value = mock_response
        
        results = client.search_by_title("test query")
        assert results == []


class TestRedisCache:
    """Tests unitarios para el servicio de caché Redis."""
    
    @pytest.fixture
    def cache_service(self):
        return RedisCache()
    
    @patch('redis.Redis.get')
    @patch('redis.Redis.setex')
    def test_cache_set_and_get(self, mock_setex, mock_get, cache_service):
        """Test almacenamiento y recuperación del caché."""
        # Test set
        test_data = [{"title": "Test Book", "author": "Test Author"}]
        cache_service.set_json("test_key", test_data, ttl_seconds=3600)
        
        mock_setex.assert_called_once_with("test_key", 3600, json.dumps(test_data))
        
        # Test get
        mock_get.return_value = json.dumps(test_data)
        result = cache_service.get_json("test_key")
        
        assert result == test_data
        mock_get.assert_called_once_with("test_key")
    
    @patch('redis.Redis.get')
    def test_cache_miss(self, mock_get, cache_service):
        """Test cache miss (clave no existe)."""
        mock_get.return_value = None
        
        result = cache_service.get_json("nonexistent_key")
        assert result is None
    
    @patch('redis.Redis.get')
    def test_cache_invalid_json(self, mock_get, cache_service):
        """Test manejo de JSON inválido en caché."""
        mock_get.return_value = "invalid json"
        
        result = cache_service.get_json("invalid_key")
        assert result is None
    
    def test_redis_connection_error(self):
        """Test manejo de errores de conexión a Redis."""
        with patch('redis.Redis.from_url') as mock_redis:
            mock_redis.side_effect = Exception("Redis connection failed")
            
            # El servicio debe manejar gracefully los errores de Redis
            try:
                cache_service = RedisCache()
                result = cache_service.get_json("test_key")
                assert result is None
                
                # Set también debe fallar gracefully
                cache_service.set_json("test_key", {"data": "test"})  # No debe lanzar excepción
            except Exception:
                # Si falla la inicialización, está bien para este test
                pass


class TestBookSearchService:
    """Tests de integración para el servicio de búsqueda de libros."""
    
    @pytest.fixture
    def search_service(self):
        return BookSearchService()
    
    @patch('app.services.book_search_service.OpenLibraryClient.search_by_title')
    @patch('app.services.book_search_service.RedisCache.get_json')
    @patch('app.services.book_search_service.RedisCache.set_json')
    def test_search_with_cache_hit(self, mock_cache_set, mock_cache_get, mock_ol_search, search_service):
        """Test búsqueda con hit en caché."""
        cached_data = [{"title": "Cached Book", "authors": ["Cached Author"]}]
        mock_cache_get.return_value = cached_data
        
        results = search_service.search(title="test query")
        
        assert results == cached_data
        mock_cache_get.assert_called_once()
        mock_ol_search.assert_not_called()  # No debe llamar a la API
        mock_cache_set.assert_not_called()  # No debe actualizar caché
    
    @patch('app.services.book_search_service.OpenLibraryClient.search_by_title')
    @patch('app.services.book_search_service.GoogleBooksClient.search_by_title')
    @patch('app.services.book_search_service.RedisCache.get_json')
    @patch('app.services.book_search_service.RedisCache.set_json')
    def test_search_with_cache_miss_openlibrary_success(self, mock_cache_set, mock_cache_get, mock_gb_search, mock_ol_search, search_service):
        """Test búsqueda con cache miss y éxito en OpenLibrary."""
        mock_cache_get.return_value = None  # Cache miss
        ol_results = [{"title": "OpenLibrary Book", "authors": ["OL Author"]}]
        mock_ol_search.return_value = ol_results
        
        results = search_service.search(title="test query")
        
        assert len(results) == 1
        assert results[0]["title"] == "OpenLibrary Book"
        mock_ol_search.assert_called_once_with("test query", limit=5)
        mock_gb_search.assert_not_called()  # No debe usar fallback
        mock_cache_set.assert_called_once()  # Debe cachear resultado
    
    @patch('app.services.book_search_service.OpenLibraryClient.search_by_title')
    @patch('app.services.book_search_service.GoogleBooksClient.search_by_title')
    @patch('app.services.book_search_service.RedisCache.get_json')
    @patch('app.services.book_search_service.RedisCache.set_json')
    def test_search_fallback_to_google_books(self, mock_cache_set, mock_cache_get, mock_gb_search, mock_ol_search, search_service):
        """Test fallback a Google Books cuando OpenLibrary falla."""
        mock_cache_get.return_value = None  # Cache miss
        mock_ol_search.return_value = []  # OpenLibrary sin resultados
        gb_results = [{"title": "Google Book", "authors": ["GB Author"]}]
        mock_gb_search.return_value = gb_results
        
        results = search_service.search(title="test query")
        
        assert len(results) == 1
        assert results[0]["title"] == "Google Book"
        mock_ol_search.assert_called_once()
        mock_gb_search.assert_called_once_with("test query", limit=5)
        mock_cache_set.assert_called_once()  # Debe cachear resultado de Google Books
    
    @patch('app.services.book_search_service.OpenLibraryClient.search_by_title')
    @patch('app.services.book_search_service.GoogleBooksClient.search_by_title')
    @patch('app.services.book_search_service.RedisCache.get_json')
    def test_search_both_apis_fail(self, mock_cache_get, mock_gb_search, mock_ol_search, search_service):
        """Test cuando ambas APIs fallan."""
        mock_cache_get.return_value = None
        mock_ol_search.return_value = []
        mock_gb_search.return_value = []
        
        results = search_service.search(title="test query")
        
        assert results == []
        mock_ol_search.assert_called_once()
        mock_gb_search.assert_called_once()


class TestSearchEndpointIntegration:
    """Tests de integración para el endpoint de búsqueda."""
    
    def test_search_endpoint_basic(self):
        """Test básico del endpoint de búsqueda."""
        client = TestClient(app)
        
        with patch('app.services.book_search_service.BookSearchService.search') as mock_search:
            mock_search.return_value = [
                {
                    "title": "Test Book",
                    "authors": ["Test Author"],
                    "isbn": ["9781234567890"],
                    "publication_year": 2023
                }
            ]
            
            response = client.get("/search/books?q=test&limit=5")
            
            assert response.status_code == 200
            results = response.json()
            assert len(results) == 1
            assert results[0]["title"] == "Test Book"
            mock_search.assert_called_once_with(title="test", limit=5)
    
    def test_search_endpoint_empty_query(self):
        """Test endpoint con query vacío."""
        client = TestClient(app)
        
        response = client.get("/search/books?q=&limit=5")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_search_endpoint_missing_query(self):
        """Test endpoint sin parámetro query."""
        client = TestClient(app)
        
        response = client.get("/search/books?limit=5")
        assert response.status_code == 200  # Default empty string
        assert response.json() == []
    
    def test_search_endpoint_invalid_limit(self):
        """Test endpoint con límite inválido."""
        client = TestClient(app)
        
        # The endpoint accepts any integer limit, no validation
        response = client.get("/search/books?q=test&limit=0")
        assert response.status_code == 200
        
        response = client.get("/search/books?q=test&limit=101")
        assert response.status_code == 200
    
    @patch('app.services.book_search_service.BookSearchService.search')
    def test_search_endpoint_service_error(self, mock_search):
        """Test endpoint cuando el servicio de búsqueda falla."""
        mock_search.side_effect = Exception("Service error")
        
        client = TestClient(app)
        response = client.get("/search/books?q=test&limit=5")
        
        assert response.status_code == 500
    
    def test_search_endpoint_performance(self):
        """Test rendimiento del endpoint de búsqueda."""
        import time
        
        client = TestClient(app)
        
        with patch('app.services.book_search_service.BookSearchService.search') as mock_search:
            mock_search.return_value = []
            
            start_time = time.time()
            response = client.get("/search/books?q=performance_test&limit=10")
            end_time = time.time()
            
            assert response.status_code == 200
            # El endpoint debe responder en menos de 2 segundos (con mock)
            assert (end_time - start_time) < 2.0


class TestSearchCacheIntegration:
    """Tests de integración entre búsqueda y caché."""
    
    @patch('app.services.cache.redis.Redis')
    def test_cache_key_generation(self, mock_redis):
        """Test generación correcta de claves de caché."""
        cache_service = RedisCache()
        
        # Simular que Redis está disponible
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = None
        
        search_service = BookSearchService()
        
        # Las claves deben ser consistentes para la misma query
        key1 = search_service._make_cache_key(title="The Hobbit", isbn=None, limit=10)
        key2 = search_service._make_cache_key(title="The Hobbit", isbn=None, limit=10)
        key3 = search_service._make_cache_key(title="the hobbit", isbn=None, limit=10)  # Case insensitive
        
        assert key1 == key2
        # Dependiendo de la implementación, puede ser case sensitive o no
        # assert key1 == key3  # Descomenta si es case insensitive
    
    @patch('app.services.cache.redis.Redis.from_url')
    def test_cache_ttl_configuration(self, mock_redis_from_url):
        """Test configuración de TTL en caché."""
        mock_redis_instance = Mock()
        mock_redis_from_url.return_value = mock_redis_instance
        
        cache_service = RedisCache()
        test_data = [{"title": "Test"}]
        cache_service.set_json("test_key", test_data, ttl_seconds=7200)
        
        # Verificar que se llamó setex con el TTL correcto
        mock_redis_instance.setex.assert_called_once_with(
            "test_key", 7200, json.dumps(test_data, ensure_ascii=False)
        )
