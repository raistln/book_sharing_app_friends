"""
Tests para el sistema de escaneo de libros (códigos de barras + OCR).
"""
import pytest
from unittest.mock import Mock, patch
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
        
        assert result["success"] is False
        assert result["method"] is None
        assert result["isbn"] is None
        assert result["title"] is None
        assert result["author"] is None
        assert result["search_results"] == []
        assert "error" in result

    def test_scan_multiple_methods_empty_image(self):
        """Test escaneo múltiple con imagen vacía."""
        service = BookScanService()
        result = service.scan_multiple_methods(b"")
        
        assert result["barcode"]["success"] is False
        assert result["ocr"]["success"] is False
        assert result["recommended_method"] is None
        assert result["search_results"] == []

    @patch('app.services.book_scan_service.BookSearchService')
    def test_scan_book_with_mock_barcode(self, mock_search_service):
        """Test escaneo con código de barras simulado."""
        # Mock del scanner de códigos de barras
        mock_scanner = Mock()
        mock_scanner.extract_isbn.return_value = "9780261102217"
        
        # Mock del servicio de búsqueda
        mock_search_service.return_value.search.return_value = [
            {"title": "The Hobbit", "authors": ["J.R.R. Tolkien"]}
        ]
        
        service = BookScanService(
            barcode_scanner=mock_scanner,
            search_service=mock_search_service.return_value
        )
        
        result = service.scan_book(b"fake_image_data")
        
        assert result["success"] is True
        assert result["method"] == "barcode"
        assert result["isbn"] == "9780261102217"
        assert result["title"] == "The Hobbit"
        assert result["author"] == "J.R.R. Tolkien"
        assert len(result["search_results"]) == 1

    @patch('app.services.book_scan_service.BookSearchService')
    def test_scan_book_with_mock_ocr(self, mock_search_service):
        """Test escaneo con OCR simulado."""
        # Mock del scanner de códigos de barras (sin resultados)
        mock_scanner = Mock()
        mock_scanner.extract_isbn.return_value = None
        
        # Mock del servicio OCR
        mock_ocr = Mock()
        mock_ocr.extract_book_title.return_value = "The Lord of the Rings"
        mock_ocr.extract_author.return_value = "J.R.R. Tolkien"
        
        # Mock del servicio de búsqueda
        mock_search_service.return_value.search.return_value = [
            {"title": "The Lord of the Rings", "authors": ["J.R.R. Tolkien"]}
        ]
        
        service = BookScanService(
            barcode_scanner=mock_scanner,
            ocr_service=mock_ocr,
            search_service=mock_search_service.return_value
        )
        
        result = service.scan_book(b"fake_image_data")
        
        assert result["success"] is True
        assert result["method"] == "ocr"
        assert result["isbn"] is None
        assert result["title"] == "The Lord of the Rings"
        assert result["author"] == "J.R.R. Tolkien"
        assert len(result["search_results"]) == 1
