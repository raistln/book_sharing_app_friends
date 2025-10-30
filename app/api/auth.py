"""
Módulo de autenticación y gestión de usuarios.

Este módulo proporciona endpoints para el registro de nuevos usuarios, inicio de sesión,
obtención de tokens de acceso y gestión del perfil del usuario autenticado.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import Token
from app.schemas.error import ErrorResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_access_token,
    get_current_user,
)
from app.models.user import User
from app.utils.rate_limiter import auth_rate_limit
from app.utils.logger import log_endpoint_call, log_auth_attempt


router = APIRouter(
    prefix="/auth",
    tags=["autenticación"],
    responses={
        401: {"description": "No autorizado - Credenciales inválidas o faltantes"},
        422: {"description": "Error de validación en los datos de entrada"},
        429: {"description": "Demasiadas solicitudes - Límite de tasa excedido"},
        500: {"description": "Error interno del servidor"}
    },
)
logger = logging.getLogger("book_sharing.auth")


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="""
    Crea una nueva cuenta de usuario en el sistema.
    
    Este endpoint permite a los usuarios registrarse en la plataforma proporcionando
    la información básica requerida. Se aplican validaciones para asegurar la seguridad
    de las contraseñas y la unicidad de nombres de usuario y correos electrónicos.
    """,
    responses={
        201: {
            "description": "Usuario registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "usuario_nuevo",
                        "email": "usuario@ejemplo.com",
                        "full_name": "Juan Pérez",
                        "is_active": True,
                        "is_superuser": False,
                        "created_at": "2025-09-23T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Datos de usuario inválidos o incompletos",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "El nombre de usuario ya está en uso"}
                }
            }
        },
        422: {
            "description": "Error de validación en los datos de entrada",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "password"], "msg": "La contraseña es muy corta", "type": "value_error"}]}
                }
            }
        },
        429: {
            "description": "Demasiadas solicitudes",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Demasiadas solicitudes. Por favor, intente de nuevo más tarde."}
                }
            }
        }
    }
)
@auth_rate_limit()
@log_endpoint_call("/auth/register", "POST")
async def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Register user username=%s email=%s from IP=%s", user_in.username, user_in.email, client_ip)
    
    try:
        user = register_user(db=db, user_in=user_in)
        log_auth_attempt(user_in.username, True, client_ip)
        return user
    except Exception as e:
        log_auth_attempt(user_in.username, False, client_ip)
        raise


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="""
    Autentica a un usuario y devuelve un token de acceso JWT.

    Este endpoint valida las credenciales del usuario (nombre de usuario o email y contraseña)
    y, si son correctas, genera un token JWT que puede ser utilizado para autenticar
    solicitudes posteriores a la API.

    El token debe incluirse en el encabezado de autorización como:
    `Authorization: Bearer <token>`
    """,
    responses={
        200: {
            "description": "Autenticación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Credenciales inválidas",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Credenciales inválidas"}
                }
            }
        },
        422: {
            "description": "Formato de usuario o contraseña inválido",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Formato de usuario inválido"}
                }
            }
        },
        429: {
            "description": "Demasiados intentos de inicio de sesión",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Demasiados intentos. Por favor, intente de nuevo más tarde."}
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Error interno del servidor"}
                }
            }
        }
    }
)
@auth_rate_limit()
@log_endpoint_call("/auth/login", "POST")
async def login(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    # Log detallado de lo que recibe la petición
    logger.info("=== LOGIN ATTEMPT START ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.headers.get('content-type', 'Not specified')}")

    try:
        # Obtener el cuerpo de la petición como texto primero
        body = await request.body()
        logger.info(f"Raw request body: {body}")

        if not body:
            logger.error("Empty request body")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Request body is empty")

        # Intentar parsear como JSON
        try:
            import json
            json_data = json.loads(body)
            logger.info(f"Parsed JSON data: {json_data}")

            username = json_data.get("username")
            password = json_data.get("password")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw body that failed to parse: {body}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid JSON format")

    except Exception as e:
        logger.error(f"Error reading request body: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error reading request")

    logger.info(f"Extracted credentials - username: '{username}', password: '{password or 'None'}'")

    if not username or not password:
        logger.error(f"Missing credentials - username: '{username}', password: '{password}'")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Usuario y contraseña requeridos")

    logger.info(f"Login attempt username={username} from IP={client_ip}")

    # Validate username/email format to prevent SQL injection
    import re
    # Permitir username o email
    is_email = '@' in username
    if is_email:
        # Validación básica de email
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', username):
            log_auth_attempt(username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email format")
    else:
        # Validación de username
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            log_auth_attempt(username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid username format")

    # Check for SQL injection patterns
    sql_patterns = [
        r"'.*'", r'".*"', r'--', r'/\*.*\*/',
        r'\bDROP\b', r'\bDELETE\b', r'\bUNION\b', r'\bSELECT\b',
        r'\bINSERT\b', r'\bUPDATE\b', r'\bCREATE\b', r'\bALTER\b'
    ]

    for pattern in sql_patterns:
        if re.search(pattern, username, re.IGNORECASE):
            log_auth_attempt(username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid username format")

    try:
        user = authenticate_user(db=db, username=username, password=password)
        if not user:
            log_auth_attempt(username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

        access_token = create_user_access_token(user)
        log_auth_attempt(username, True, client_ip)
        logger.info("=== LOGIN ATTEMPT SUCCESS ===")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        log_auth_attempt(username, False, client_ip)
        logger.error(f"Login error for {username}: {str(e)}")
        logger.info("=== LOGIN ATTEMPT FAILED ===")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@router.post(
    "/token",
    response_model=Token,
    include_in_schema=False,  # Ocultar de la documentación principal para evitar duplicados
    summary="Alias para /login (compatibilidad OAuth2)",
    description="""
    Este endpoint es un alias de /login para mantener compatibilidad con clientes OAuth2
    que esperan usar el endpoint estándar /token.

    Es funcionalmente idéntico a /login y acepta los mismos parámetros.
    """,
    responses={
        200: {
            "description": "Autenticación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        429: {"$ref": "#/components/responses/TooManyRequestsError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    }
)
@auth_rate_limit()
async def token_alias(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Alias para el endpoint de login, compatible con OAuth2.

    Este endpoint es idéntico a /login pero responde en /token para compatibilidad
    con clientes que esperan la ruta estándar de OAuth2.
    """
    return await login(request=request, form_data=form_data, db=db)


@router.get(
    "/me",
    response_model=UserSchema,
    summary="Obtener perfil del usuario actual",
    description="""
    Devuelve la información del perfil del usuario autenticado.
    
    Este endpoint requiere autenticación mediante token JWT en el encabezado de autorización.
    """,
    responses={
        200: {
            "description": "Perfil del usuario obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "usuario_ejemplo",
                        "email": "usuario@ejemplo.com",
                        "full_name": "Juan Pérez",
                        "is_active": True,
                        "is_superuser": False,
                        "created_at": "2025-01-01T12:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "No autenticado o token inválido",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "No autenticado"}
                }
            }
        },
        403: {
            "description": "Usuario inactivo o sin permisos",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario inactivo"}
                }
            }
        }
    }
)
async def read_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.
    
    Args:
        current_user: Usuario autenticado obtenido del token JWT.
        
    Returns:
        User: Información del perfil del usuario autenticado.
    """
    return current_user


