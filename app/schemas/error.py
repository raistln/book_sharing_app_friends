"""
Esquemas para respuestas de error estandarizadas en la API.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detalle de un error de validación o de negocio."""
    loc: List[str] = Field(
        ...,
        example=["body", "password"],
        description="Ubicación del error en la solicitud"
    )
    msg: str = Field(
        ...,
        example="La contraseña es demasiado corta",
        description="Mensaje descriptivo del error"
    )
    type: str = Field(
        ...,
        example="value_error",
        description="Tipo de error"
    )


class ErrorResponse(BaseModel):
    """Respuesta estándar para errores de la API."""
    detail: Any = Field(
        ...,
        example="Error de autenticación",
        description="Mensaje de error o lista de errores de validación"
    )


class HTTPError(BaseModel):
    """Modelo para documentar respuestas de error HTTP."""
    detail: str = Field(
        ...,
        example="Error de autenticación",
        description="Descripción del error"
    )


# Respuestas de error comunes para la documentación de la API
responses = {
    400: {
        "model": HTTPError,
        "description": "Solicitud incorrecta - Parámetros inválidos o faltantes"
    },
    401: {
        "model": HTTPError,
        "description": "No autorizado - Credenciales inválidas o faltantes"
    },
    403: {
        "model": HTTPError,
        "description": "Prohibido - No tiene permisos para acceder al recurso"
    },
    404: {
        "model": HTTPError,
        "description": "No encontrado - El recurso solicitado no existe"
    },
    409: {
        "model": HTTPError,
        "description": "Conflicto - El recurso ya existe o hay un conflicto con el estado actual"
    },
    422: {
        "model": ErrorResponse,
        "description": "Error de validación - Los datos proporcionados no son válidos"
    },
    429: {
        "model": HTTPError,
        "description": "Demasiadas solicitudes - Límite de tasa excedido"
    },
    500: {
        "model": HTTPError,
        "description": "Error interno del servidor - Ocurrió un error inesperado"
    },
    503: {
        "model": HTTPError,
        "description": "Servicio no disponible - El servicio no está disponible en este momento"
    }
}
