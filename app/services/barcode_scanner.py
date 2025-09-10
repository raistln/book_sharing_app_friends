"""
Servicio para escanear códigos de barras en imágenes de libros.
"""
import cv2
import numpy as np
from typing import List, Optional
from pyzbar import pyzbar
import logging

logger = logging.getLogger(__name__)


class BarcodeScanner:
    def __init__(self):
        self.supported_formats = ['EAN13', 'EAN8', 'ISBN13', 'ISBN10', 'UPC_A', 'UPC_E']

    def scan_barcodes(self, image_data: bytes) -> List[str]:
        """
        Escanea códigos de barras en una imagen.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            Lista de códigos encontrados (ISBNs, EANs, etc.)
        """
        try:
            # Convertir bytes a imagen OpenCV
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.warning("No se pudo decodificar la imagen")
                return []
            
            # Detectar códigos de barras
            barcodes = pyzbar.decode(image)
            
            codes = []
            for barcode in barcodes:
                # Obtener el tipo y datos del código
                barcode_type = barcode.type
                barcode_data = barcode.data.decode('utf-8')
                
                logger.info(f"Código detectado: {barcode_type} = {barcode_data}")
                
                # Filtrar solo códigos de libros
                if barcode_type in self.supported_formats:
                    codes.append(barcode_data)
            
            return codes
            
        except Exception as e:
            logger.error(f"Error escaneando códigos de barras: {e}")
            return []

    def extract_isbn(self, image_data: bytes) -> Optional[str]:
        """
        Extrae el ISBN de una imagen de libro.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            ISBN encontrado o None
        """
        codes = self.scan_barcodes(image_data)
        
        # Buscar ISBN en los códigos encontrados
        for code in codes:
            # Limpiar el código (quitar guiones, espacios)
            clean_code = code.replace('-', '').replace(' ', '')
            
            # Verificar si es un ISBN válido (10 o 13 dígitos)
            if clean_code.isdigit() and len(clean_code) in [10, 13]:
                return clean_code
        
        return None

    def is_isbn(self, code: str) -> bool:
        """
        Verifica si un código es un ISBN válido.
        
        Args:
            code: Código a verificar
            
        Returns:
            True si es ISBN válido
        """
        clean_code = code.replace('-', '').replace(' ', '')
        return clean_code.isdigit() and len(clean_code) in [10, 13]
