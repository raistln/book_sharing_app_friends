"""
Pruebas unitarias para OCRService
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.ocr_service import OCRService


class TestOCRService:
    def test_extract_text_from_image_valid(self):
        """Test extract_text_from_image with valid image"""
        service = OCRService()

        # Mock the entire OCR process
        with patch.object(service.reader, 'readtext', return_value=[((0, 0, 10, 10), "Hello World", 0.9)]), \
             patch('app.services.ocr_service.cv2.imdecode') as mock_imdecode, \
             patch('app.services.ocr_service.np.frombuffer') as mock_frombuffer:

            mock_image = MagicMock()
            mock_image.shape = (100, 100, 3)  # Añadir dimensiones reales para evitar errores en comparaciones
            mock_imdecode.return_value = mock_image
            mock_frombuffer.return_value = b'fake_data'

            result = service.extract_text_from_image(b'fake_image_data')

            assert result == "Hello World"
            service.reader.readtext.assert_called_once_with(mock_image)

    def test_extract_text_from_image_invalid_image(self):
        """Test extract_text_from_image with invalid image"""
        service = OCRService()

        with patch('cv2.imdecode') as mock_imdecode:
            mock_imdecode.return_value = None  # Invalid image

            result = service.extract_text_from_image(b'invalid_data')

            assert result == ""

    def test_extract_text_from_image_exception(self):
        """Test extract_text_from_image with exception"""
        service = OCRService()

        with patch('cv2.imdecode', side_effect=Exception("CV2 Error")):
            result = service.extract_text_from_image(b'data')

            assert result == ""

    def test_extract_book_title_no_text(self):
        """Test extract_book_title with no text"""
        service = OCRService()

        with patch.object(service, 'extract_text_from_image', return_value=""):
            result = service.extract_book_title(b'data')

            assert result is None

    def test_extract_author_with_by(self):
        """Test extract_author with 'by' keyword"""
        service = OCRService()

        with patch.object(service, 'extract_text_from_image', return_value="The Great Gatsby\nby F. Scott Fitzgerald"):
            result = service.extract_author(b'data')

            assert result == "F. Scott Fitzgerald"

    def test_extract_author_no_match(self):
        """Test extract_author with no author pattern"""
        service = OCRService()

        with patch.object(service, 'extract_text_from_image', return_value="Just some text without author"):
            result = service.extract_author(b'data')

            assert result is None

    def test_extract_author_multiple_keywords(self):
        """Test extract_author with multiple keywords"""
        service = OCRService()

        with patch.object(service, 'extract_text_from_image', return_value="Book by John Doe\nAuthor: Jane Smith"):
            # Should find first match
            result = service.extract_author(b'data')
            assert result == "John Doe"  # 'by' comes first
