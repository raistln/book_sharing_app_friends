"""
Servicio para extraer texto de imágenes de libros usando EasyOCR.
"""
import easyocr
import cv2
import numpy as np
from typing import List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self, languages: List[str] = None):
        """
        Inicializa el servicio OCR.
        
        Args:
            languages: Lista de idiomas para OCR (por defecto ['en', 'es'])
        """
        self.languages = languages or ['en', 'es']
        self.reader = easyocr.Reader(self.languages, gpu=False)
        
    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extrae texto de una imagen.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            Texto extraído
        """
        try:
            # Convertir bytes a imagen OpenCV
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.warning("No se pudo decodificar la imagen")
                return ""
            
            # Procesar con EasyOCR
            results = self.reader.readtext(image)
            
            # Extraer texto de los resultados
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filtrar por confianza
                    text_parts.append(text.strip())
            
            full_text = " ".join(text_parts)
            logger.info(f"Texto extraído: {full_text[:100]}...")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            return ""

    def extract_book_title(self, image_data: bytes) -> Optional[str]:
        """
        Extrae el título del libro de una imagen.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            Título del libro o None
        """
        text = self.extract_text_from_image(image_data)
        
        if not text:
            return None
        
        # Limpiar y normalizar texto
        clean_text = re.sub(r'\s+', ' ', text.strip())
        
        # Heurísticas para encontrar el título:
        # 1. Buscar líneas que parezcan títulos (mayúsculas, longitud)
        lines = clean_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:  # Longitud razonable
                # Si la línea tiene muchas mayúsculas, podría ser título
                if sum(1 for c in line if c.isupper()) > len(line) * 0.3:
                    return line
                # Si es la primera línea significativa, podría ser título
                if len(line) > 10:
                    return line
        
        # Si no encontramos nada específico, devolver las primeras palabras
        words = clean_text.split()
        if len(words) > 2:
            return " ".join(words[:5])  # Primeras 5 palabras
        
        return clean_text[:50] if clean_text else None

    def extract_author(self, image_data: bytes) -> Optional[str]:
        """
        Extrae el autor del libro de una imagen.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            Autor del libro o None
        """
        text = self.extract_text_from_image(image_data)
        
        if not text:
            return None
        
        # Buscar patrones comunes de autor
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Buscar líneas que contengan "by", "por", "autor", etc.
            if any(keyword in line.lower() for keyword in ['by', 'por', 'autor', 'author']):
                # Extraer el nombre después de la palabra clave
                for keyword in ['by', 'por', 'autor', 'author']:
                    if keyword in line.lower():
                        parts = line.lower().split(keyword)
                        if len(parts) > 1:
                            author = parts[1].strip()
                            if len(author) > 2:
                                return author.title()
        
        return None
