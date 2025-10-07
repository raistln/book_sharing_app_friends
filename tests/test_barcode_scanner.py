"""
Pruebas unitarias para BarcodeScanner
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.barcode_scanner import BarcodeScanner


class TestBarcodeScanner:
    def test_scan_barcodes_valid_image(self):
        """Test scan_barcodes with valid image containing barcode"""
        scanner = BarcodeScanner()

        with patch('app.services.barcode_scanner.cv2.imdecode') as mock_imdecode, \
             patch('app.services.barcode_scanner.pyzbar.decode') as mock_decode, \
             patch('app.services.barcode_scanner.np.frombuffer') as mock_frombuffer:

            mock_image = MagicMock()
            mock_imdecode.return_value = mock_image
            mock_frombuffer.return_value = b'fake_data'

            mock_barcode = MagicMock()
            mock_barcode.type = 'EAN13'
            mock_barcode.data.decode.return_value = '9781234567890'
            mock_decode.return_value = [mock_barcode]

            result = scanner.scan_barcodes(b'fake_image')

            assert len(result) == 1
            assert result[0] == '9781234567890'

    def test_scan_barcodes_invalid_image(self):
        """Test scan_barcodes with invalid image"""
        scanner = BarcodeScanner()

        with patch('app.services.barcode_scanner.cv2.imdecode') as mock_imdecode:
            mock_imdecode.return_value = None

            result = scanner.scan_barcodes(b'invalid')

            assert result == []

    def test_scan_barcodes_exception(self):
        """Test scan_barcodes with exception"""
        scanner = BarcodeScanner()

        with patch('app.services.barcode_scanner.cv2.imdecode', side_effect=Exception("CV2 Error")):
            result = scanner.scan_barcodes(b'data')

            assert result == []

    def test_extract_isbn_valid(self):
        """Test extract_isbn with valid ISBN"""
        scanner = BarcodeScanner()

        with patch.object(scanner, 'scan_barcodes', return_value=['9781234567890']):
            result = scanner.extract_isbn(b'data')

            assert result == '9781234567890'

    def test_extract_isbn_invalid_codes(self):
        """Test extract_isbn with non-ISBN codes"""
        scanner = BarcodeScanner()

        with patch.object(scanner, 'scan_barcodes', return_value=['123456789', 'notanumber']):
            result = scanner.extract_isbn(b'data')

            assert result is None

    def test_is_isbn_valid(self):
        """Test is_isbn with valid ISBNs"""
        scanner = BarcodeScanner()

        assert scanner.is_isbn('9781234567890') == True
        assert scanner.is_isbn('1234567890') == True

    def test_is_isbn_invalid(self):
        """Test is_isbn with invalid codes"""
        scanner = BarcodeScanner()

        assert scanner.is_isbn('123') == False
        assert scanner.is_isbn('notanumber') == False
        assert scanner.is_isbn('978-12-3456-789-0') == True  # With hyphens
