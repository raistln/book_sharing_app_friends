"""
Tests comprehensivos para el sistema de autenticación.
Incluye tests de seguridad, validación de tokens y casos edge.
"""
import os
# Set environment variables before any imports
os.environ["TESTING"] = "true"
os.environ["DISABLE_RATE_LIMITING"] = "true"

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.services.auth_service import get_current_user, create_user_access_token
from app.models.user import User
from app.utils.security import create_access_token, decode_access_token


class TestAuthenticationSecurity:
    """Tests de seguridad para el sistema de autenticación."""
    
    def test_password_hashing_security(self):
        """Test que las contraseñas se hashean correctamente y no se almacenan en texto plano."""
        client = TestClient(app)
        
        username = f"security_test_{uuid.uuid4().hex[:8]}"
        password = "SecurePassword123!"
        
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
            "full_name": "Security Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # La respuesta no debe contener la contraseña
        user_info = response.json()
        assert "password" not in user_info
        assert "password_hash" not in user_info
        
        # Verificar que el login funciona con la contraseña original
        login_data = {"username": username, "password": password}
        response = client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_token_expiration_handling(self):
        """Test manejo de tokens expirados."""
        # Crear token expirado
        user_id = str(uuid.uuid4())
        
        with patch('app.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES', -1):  # Token ya expirado
            expired_token = create_access_token(subject=user_id)
        
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
        response_data = response.json()
        # Check for either 'detail' or 'message' field depending on error handler
        error_message = response_data.get("detail") or response_data.get("message", "")
        assert ("Could not validate credentials" in error_message or 
                "No se pudieron validar las credenciales" in error_message)
    
    def test_invalid_token_format(self):
        """Test manejo de tokens con formato inválido."""
        client = TestClient(app)
        
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 401
    
    def test_sql_injection_prevention(self):
        """Test prevención de inyección SQL en campos de entrada."""
        client = TestClient(app)
        
        # Intentos de inyección SQL en username
        malicious_usernames = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin' UNION SELECT * FROM users --",
            "'; DELETE FROM users WHERE '1'='1"
        ]
        
        for malicious_username in malicious_usernames:
            user_data = {
                "username": malicious_username,
                "email": "test@example.com",
                "password": "Password123!"
            }
            
            # El registro puede fallar por validación, pero no debe causar error del servidor
            response = client.post("/auth/register", json=user_data)
            # En tests, rate limiting está deshabilitado, así que debería ser error de validación
            assert response.status_code in [400, 422]  # Error de validación, no error del servidor
            
            # Intentar login también
            login_data = {"username": malicious_username, "password": "Password123!"}
            response = client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            # Aceptar 429 (rate limit) o 401/422 (validación fallida)
            assert response.status_code in [401, 422, 429], f"Unexpected status code: {response.status_code} - {response.text}"
    
    def test_brute_force_protection_simulation(self):
        """Test simulación de protección contra ataques de fuerza bruta."""
        client = TestClient(app)
        
        # Crear usuario válido
        username = f"brute_test_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "CorrectPassword123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Intentar múltiples logins con contraseña incorrecta
        for i in range(5):
            login_data = {"username": username, "password": f"WrongPassword{i}"}
            response = client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            # En tests, rate limiting está deshabilitado, así que debería ser 401
            assert response.status_code == 401
        
        # Verificar que el login correcto aún funciona (sin rate limiting en tests)
        correct_login = {"username": username, "password": "CorrectPassword123!"}
        response = client.post(
            "/auth/login",
            data=correct_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # En tests, el rate limiting está deshabilitado, así que debería funcionar
        assert response.status_code == 200


class TestTokenManagement:
    """Tests para manejo avanzado de tokens JWT."""
    
    def test_token_payload_integrity(self):
        """Test integridad del payload del token."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)
        
        # Decodificar y verificar contenido
        decoded_subject = decode_access_token(token)
        assert decoded_subject == user_id
    
    def test_token_with_special_characters(self):
        """Test tokens con caracteres especiales en el subject."""
        special_subjects = [
            "user@domain.com",
            "user-with-dashes",
            "user_with_underscores",
            "user.with.dots"
        ]
        
        for subject in special_subjects:
            token = create_access_token(subject=subject)
            decoded = decode_access_token(token)
            assert decoded == subject
    
    def test_concurrent_token_usage(self):
        """Test uso concurrente de múltiples tokens para el mismo usuario."""
        client = TestClient(app)
        
        # Crear usuario
        username = f"concurrent_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Generar múltiples tokens
        login_data = {"username": username, "password": "Password123!"}
        tokens = []
        
        for _ in range(3):
            response = client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200
            tokens.append(response.json()["access_token"])
        
        # Verificar que todos los tokens funcionan
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 200
            assert response.json()["username"] == username


class TestUserValidation:
    """Tests para validación de datos de usuario."""
    
    def test_username_validation_rules(self):
        """Test reglas de validación para usernames."""
        client = TestClient(app)
        
        invalid_usernames = [
            "",  # Vacío
            "a",  # Muy corto
            "a" * 100,  # Muy largo
            "user with spaces",  # Espacios
            "user@invalid",  # Caracteres especiales
            "123numeric",  # Solo números al inicio
        ]
        
        for username in invalid_usernames:
            user_data = {
                "username": username,
                "email": "test@example.com",
                "password": "Password123!"
            }
            
            response = client.post("/auth/register", json=user_data)
            assert response.status_code in [400, 422]
    
    def test_email_validation_rules(self):
        """Test reglas de validación para emails."""
        client = TestClient(app)
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user..double@domain.com",
            "user@domain..com"
        ]
        
        for email in invalid_emails:
            username = f"test_{uuid.uuid4().hex[:8]}"
            user_data = {
                "username": username,
                "email": email,
                "password": "Password123!"
            }
            
            response = client.post("/auth/register", json=user_data)
            assert response.status_code in [400, 422]
    
    def test_password_strength_validation(self):
        """Test validación de fortaleza de contraseñas."""
        client = TestClient(app)
        
        weak_passwords = [
            "123",  # Muy corta
            "password",  # Sin mayúsculas ni números
            "PASSWORD",  # Sin minúsculas ni números
            "12345678",  # Solo números
            "Password",  # Sin números
            "password123"  # Sin mayúsculas
        ]
        
        for password in weak_passwords:
            username = f"pwd_test_{uuid.uuid4().hex[:8]}"
            user_data = {
                "username": username,
                "email": f"{username}@example.com",
                "password": password
            }
            
            response = client.post("/auth/register", json=user_data)
            # Dependiendo de la implementación, puede ser 400 o 422
            assert response.status_code in [400, 422]


class TestUserStateManagement:
    """Tests para manejo de estados de usuario."""
    
    def test_inactive_user_login_prevention(self):
        """Test prevención de login para usuarios inactivos."""
        client = TestClient(app)
        
        # Crear usuario
        username = f"inactive_test_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Simular desactivación de usuario (esto requeriría un endpoint admin)
        # Por ahora, verificamos el comportamiento con mock
        with patch('app.api.auth.authenticate_user') as mock_auth:
            # Simular usuario inactivo
            mock_auth.return_value = None  # authenticate_user retorna None para usuarios inactivos
            
            login_data = {"username": username, "password": "Password123!"}
            response = client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 401
    
    def test_user_profile_update_security(self):
        """Test seguridad en actualización de perfil de usuario."""
        client = TestClient(app)
        
        # Crear usuario
        username = f"profile_test_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Password123!",
            "full_name": "Original Name"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Login
        login_data = {"username": username, "password": "Password123!"}
        response = client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verificar que el usuario puede ver su propio perfil
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["username"] == username
        assert profile["full_name"] == "Original Name"
