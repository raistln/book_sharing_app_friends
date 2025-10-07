"""
Pruebas unitarias para logger.py
"""
import pytest
import logging
import json
from unittest.mock import patch, MagicMock
from app.utils.logger import JSONFormatter, setup_logging, log_endpoint_call, log_auth_attempt, log_security_event, log_rate_limit_exceeded


class TestLogger:
    def test_json_formatter(self):
        """Test JSONFormatter"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test_logger', level=logging.INFO, pathname='test.py',
            lineno=10, msg='Test message', args=(), exc_info=None
        )

        result = formatter.format(record)
        log_entry = json.loads(result)

        assert log_entry['level'] == 'INFO'
        assert log_entry['logger'] == 'test_logger'
        assert log_entry['message'] == 'Test message'

    def test_json_formatter_with_extra(self):
        """Test JSONFormatter with extra fields"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test_logger', level=logging.INFO, pathname='test.py',
            lineno=10, msg='Test message', args=(), exc_info=None
        )
        record.user_id = '123'
        record.request_id = 'req_456'

        result = formatter.format(record)
        log_entry = json.loads(result)

        assert log_entry['user_id'] == '123'
        assert log_entry['request_id'] == 'req_456'

    def test_setup_logging(self):
        """Test setup_logging"""
        with patch('app.utils.logger.logs_dir') as mock_logs_dir, \
             patch('app.utils.logger.logging.FileHandler') as mock_file_handler:

            mock_logs_dir.mkdir.return_value = None

            mock_handler = MagicMock()
            mock_file_handler.return_value = mock_handler

            setup_logging("INFO", True)

            mock_file_handler.assert_called()

    @pytest.mark.asyncio
    async def test_log_endpoint_call_success(self):
        """Test log_endpoint_call on success"""
        with patch('app.utils.logger.logger') as mock_logger:
            @log_endpoint_call("/test", "GET")
            async def test_func(request):
                return {"result": "ok"}

            mock_request = MagicMock()
            mock_request.id = "user_123"

            result = await test_func(mock_request)

            assert result == {"result": "ok"}
            assert mock_logger.info.call_count == 2

    @pytest.mark.asyncio
    async def test_log_endpoint_call_failure(self):
        """Test log_endpoint_call on failure"""
        with patch('app.utils.logger.logger') as mock_logger:
            @log_endpoint_call("/test", "GET")
            async def test_func(request):
                raise ValueError("Test error")

            mock_request = MagicMock()
            mock_request.id = "user_123"

            with pytest.raises(ValueError):
                await test_func(mock_request)

            mock_logger.error.assert_called_once()

    def test_log_auth_attempt_success(self):
        """Test log_auth_attempt success"""
        with patch('app.utils.logger.logger') as mock_logger:
            log_auth_attempt("user123", True, "192.168.1.1")

            mock_logger.info.assert_called_once_with(
                "Successful login for user: user123",
                extra={'user_id': 'user123', 'ip_address': '192.168.1.1'}
            )

    def test_log_auth_attempt_failure(self):
        """Test log_auth_attempt failure"""
        with patch('app.utils.logger.logger') as mock_logger:
            log_auth_attempt("user123", False, "192.168.1.1")

            mock_logger.warning.assert_called_once_with(
                "Failed login attempt for user: user123",
                extra={'user_id': 'user123', 'ip_address': '192.168.1.1'}
            )

    def test_log_security_event(self):
        """Test log_security_event"""
        with patch('app.utils.logger.logger') as mock_logger:
            log_security_event("suspicious_activity", "Multiple failed logins", "user123")

            mock_logger.warning.assert_called_once_with(
                "Security event: suspicious_activity - Multiple failed logins",
                extra={'user_id': 'user123', 'event_type': 'suspicious_activity'}
            )

    def test_log_rate_limit_exceeded(self):
        """Test log_rate_limit_exceeded"""
        with patch('app.utils.logger.logger') as mock_logger:
            log_rate_limit_exceeded("192.168.1.1", "/api/test")

            mock_logger.warning.assert_called_once_with(
                "Rate limit exceeded from 192.168.1.1 on /api/test",
                extra={'ip_address': '192.168.1.1', 'endpoint': '/api/test'}
            )
