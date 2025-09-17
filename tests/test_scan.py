"""
Tests para el sistema de escaneo de libros (códigos de barras + OCR).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.barcode_scanner import BarcodeScanner
from app.services.ocr_service import OCRService
from app.services.book_scan_service import BookScanService


class TestBarcodeScanner:
    def test_scan_barcodes_empty_image(self):
        """Test escaneo con imagen vacía."""
        scanner = BarcodeScanner()
        result = scanner.scan_barcodes(b"")
        assert result == []

    def test_extract_isbn_empty_image(self):
        """Test extracción de ISBN con imagen vacía."""
        scanner = BarcodeScanner()
        result = scanner.extract_isbn(b"")
        assert result is None

    def test_is_isbn_valid(self):
        """Test validación de ISBN."""
        scanner = BarcodeScanner()
        assert scanner.is_isbn("9780261102217") is True
        assert scanner.is_isbn("0261102217") is True
        assert scanner.is_isbn("123") is False
        assert scanner.is_isbn("abc123") is False


class TestOCRService:
    def test_extract_text_empty_image(self):
        """Test extracción de texto con imagen vacía."""
        ocr = OCRService()
        result = ocr.extract_text_from_image(b"")
        assert result == ""

    def test_extract_book_title_empty_image(self):
        """Test extracción de título con imagen vacía."""
        ocr = OCRService()
        result = ocr.extract_book_title(b"")
        assert result is None

    def test_extract_author_empty_image(self):
        """Test extracción de autor con imagen vacía."""
        ocr = OCRService()
        result = ocr.extract_author(b"")
        assert result is None


class TestBookScanService:
    def test_scan_book_empty_image(self):
        """Test escaneo de libro con imagen vacía."""
        service = BookScanService()
        result = service.scan_book(b"")
        

    def test_scan_multiple_methods_empty_image(self):
        """Test escaneo múltiple con imagen vacía."""
        with patch('app.services.book_scan_service.BookSearchService') as mock_search_service:
            service = BookScanService()
            result = service.scan_multiple_methods(b"")
            assert isinstance(result, dict)
            assert 'barcode' in result
            assert 'ocr' in result
            assert 'search_results' in result
            assert 'recommended_method' in result
            assert result['barcode'] == {'isbn': None, 'success': False}
            assert result['ocr'] == {'title': None, 'author': None, 'success': False}
            assert result['search_results'] == []
            assert result['recommended_method'] is None

    @patch('app.services.book_scan_service.BookSearchService')
    def test_scan_book_with_mock_barcode(self, mock_search_service):
        """Test escaneo con código de barras simulado."""
        # Configurar mocks
        mock_barcode_scanner = Mock()
        mock_barcode_scanner.extract_isbn.return_value = "9780261102217"
        
        mock_search = Mock()
        mock_search.search.return_value = [{"title": "Test Book"}]
        mock_search_service.return_value = mock_search
        
        # Inyectar mock
        service = BookScanService()
        service.barcode_scanner = mock_barcode_scanner
        
        # Probar
        result = service.scan_book(b"fake_image")
        
        # Verificar la estructura del resultado
        assert isinstance(result, dict)
        assert result['method'] == 'barcode'
        assert result['isbn'] == '9780261102217'
        assert result['title'] == 'Test Book'
        assert result['author'] is None
        assert result['search_results'] == [{'title': 'Test Book'}]
        assert result['success'] is True
        assert 'error' in result
        
        # Verificar llamadas a los mocks
        mock_barcode_scanner.extract_isbn.assert_called_once_with(b"fake_image")
        mock_search.search.assert_called_once_with(isbn="9780261102217", limit=5)

    @patch('app.services.book_scan_service.BookSearchService')
    def test_scan_book_with_mock_ocr(self, mock_search_service):
        """Test escaneo con OCR simulado."""
        # Configurar mocks
        mock_barcode_scanner = Mock()
        mock_barcode_scanner.extract_isbn.return_value = None  # Simular que no hay código de barras
        
        # Configurar el mock de OCR para devolver un título y autor
        mock_ocr = Mock()
        mock_ocr.extract_book_title.return_value = "Sample Book Title"
        mock_ocr.extract_author.return_value = "Sample Author"
        
        # Configurar el mock del servicio de búsqueda
        mock_search = Mock()
        mock_search.search.return_value = [{"title": "Sample Book Title", "authors": ["Sample Author"]}]
        mock_search_service.return_value = mock_search
        
        # Inyectar mocks
        service = BookScanService()
        service.barcode_scanner = mock_barcode_scanner
        service.ocr_service = mock_ocr  # Asegurarse de usar el nombre correcto del atributo
        
        # Probar
        result = service.scan_book(b"fake_image")
        
        # Verificar la estructura del resultado
        assert isinstance(result, dict)
        assert result['method'] == 'ocr'  # Debería ser 'ocr' si el OCR tiene éxito
        assert result['isbn'] is None
        assert result['title'] == 'Sample Book Title'
        assert result['author'] == 'Sample Author'
        assert result['search_results'] == [{'title': 'Sample Book Title', 'authors': ['Sample Author']}]
        assert result['success'] is True
        assert 'error' not in result or result['error'] is None
        
        # Verificar llamadas a los mocks
        mock_barcode_scanner.extract_isbn.assert_called_once_with(b"fake_image")
        mock_ocr.extract_book_title.assert_called_once_with(b"fake_image")
        mock_ocr.extract_author.assert_called_once_with(b"fake_image")
        mock_search.search.assert_called_once_with(title="Sample Book Title", limit=5)

    @patch('app.services.book_scan_service.BookSearchService')
    def test_scan_book_with_mock_barcode_and_ocr(self, mock_search_service):
        """Test escaneo con código de barras y OCR simulados."""
        # Configurar mocks
        mock_barcode_scanner = Mock()
        mock_barcode_scanner.extract_isbn.return_value = "9780261102217"  # Simular código de barras encontrado
        
        # Configurar el mock de OCR (no debería usarse si el código de barras tiene éxito)
        mock_ocr = Mock()
        mock_ocr.extract_book_title.return_value = "Sample Book Title"
        mock_ocr.extract_author.return_value = "Sample Author"
        
        # Configurar el mock del servicio de búsqueda
        mock_search = Mock()
        mock_search.search.return_value = [{"title": "Sample Book Title", "authors": ["Sample Author"]}]
        mock_search_service.return_value = mock_search
        
        # Inyectar mocks
        service = BookScanService()
        service.barcode_scanner = mock_barcode_scanner
        service.ocr_service = mock_ocr
        
        # Probar
        result = service.scan_book(b"fake_image")
        
        # Verificar la estructura del resultado
        assert isinstance(result, dict)
        assert result['method'] == 'barcode'  # Debería ser 'barcode' ya que tiene prioridad
        assert result['isbn'] == '9780261102217'
        assert result['title'] == 'Sample Book Title'
        assert result['author'] == 'Sample Author'
        assert result['search_results'] == [{'title': 'Sample Book Title', 'authors': ['Sample Author']}]
        assert result['success'] is True
        assert 'error' not in result or result['error'] is None
        
        # Verificar llamadas a los mocks
        mock_barcode_scanner.extract_isbn.assert_called_once_with(b"fake_image")
        
        # Verificar que los métodos de OCR NO se llamaron (ya que el código de barras tuvo éxito)
        mock_ocr.extract_book_title.assert_not_called()
        mock_ocr.extract_author.assert_not_called()
        
        # Verificar que se llamó a la búsqueda con el ISBN
        mock_search.search.assert_called_once_with(isbn="9780261102217", limit=5)
