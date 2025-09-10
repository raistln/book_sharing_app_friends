"""
Servicio unificado para escanear libros: códigos de barras + OCR.
"""
from typing import Dict, List, Optional, Any
import logging

from app.services.barcode_scanner import BarcodeScanner
from app.services.ocr_service import OCRService
from app.services.book_search_service import BookSearchService

logger = logging.getLogger(__name__)


class BookScanService:
    def __init__(
        self,
        barcode_scanner: Optional[BarcodeScanner] = None,
        ocr_service: Optional[OCRService] = None,
        search_service: Optional[BookSearchService] = None,
    ):
        self.barcode_scanner = barcode_scanner or BarcodeScanner()
        self.ocr_service = ocr_service or OCRService()
        self.search_service = search_service or BookSearchService()

    def scan_book(self, image_data: bytes) -> Dict[str, Any]:
        """
        Escanea un libro usando códigos de barras y OCR.
        
        Args:
            image_data: Bytes de la imagen del libro
            
        Returns:
            Diccionario con resultados del escaneo
        """
        logger.info("Iniciando escaneo de libro")
        
        result = {
            "method": None,
            "isbn": None,
            "title": None,
            "author": None,
            "search_results": [],
            "success": False,
            "error": None
        }
        
        try:
            # 1. Intentar escanear código de barras primero (más confiable)
            isbn = self.barcode_scanner.extract_isbn(image_data)
            
            if isbn:
                logger.info(f"ISBN encontrado por código de barras: {isbn}")
                result["method"] = "barcode"
                result["isbn"] = isbn
                result["success"] = True
                
                # Buscar libro por ISBN
                search_results = self.search_service.search(isbn=isbn, limit=5)
                result["search_results"] = search_results
                
                if search_results:
                    # Usar datos de la búsqueda
                    first_result = search_results[0]
                    result["title"] = first_result.get("title")
                    result["author"] = first_result.get("authors", [None])[0] if first_result.get("authors") else None
                
                return result
            
            # 2. Si no hay código de barras, usar OCR
            logger.info("No se encontró código de barras, intentando OCR")
            
            # Extraer título con OCR
            title = self.ocr_service.extract_book_title(image_data)
            author = self.ocr_service.extract_author(image_data)
            
            if title:
                logger.info(f"Título extraído por OCR: {title}")
                result["method"] = "ocr"
                result["title"] = title
                result["author"] = author
                result["success"] = True
                
                # Buscar libro por título
                search_results = self.search_service.search(title=title, limit=5)
                result["search_results"] = search_results
                
                return result
            
            # 3. Si no se encontró nada
            result["error"] = "No se pudo extraer información del libro"
            logger.warning("No se pudo extraer información del libro")
            
        except Exception as e:
            result["error"] = f"Error durante el escaneo: {str(e)}"
            logger.error(f"Error durante el escaneo: {e}")
        
        return result

    def scan_multiple_methods(self, image_data: bytes) -> Dict[str, Any]:
        """
        Escanea un libro usando todos los métodos disponibles.
        
        Args:
            image_data: Bytes de la imagen del libro
            
        Returns:
            Diccionario con resultados de todos los métodos
        """
        logger.info("Iniciando escaneo múltiple de libro")
        
        result = {
            "barcode": {
                "isbn": None,
                "success": False
            },
            "ocr": {
                "title": None,
                "author": None,
                "success": False
            },
            "search_results": [],
            "recommended_method": None
        }
        
        try:
            # Escanear código de barras
            isbn = self.barcode_scanner.extract_isbn(image_data)
            if isbn:
                result["barcode"]["isbn"] = isbn
                result["barcode"]["success"] = True
                result["recommended_method"] = "barcode"
                
                # Buscar por ISBN
                search_results = self.search_service.search(isbn=isbn, limit=5)
                result["search_results"] = search_results
                
                return result
            
            # Escanear con OCR
            title = self.ocr_service.extract_book_title(image_data)
            author = self.ocr_service.extract_author(image_data)
            
            if title:
                result["ocr"]["title"] = title
                result["ocr"]["author"] = author
                result["ocr"]["success"] = True
                result["recommended_method"] = "ocr"
                
                # Buscar por título
                search_results = self.search_service.search(title=title, limit=5)
                result["search_results"] = search_results
            
        except Exception as e:
            logger.error(f"Error durante escaneo múltiple: {e}")
        
        return result
