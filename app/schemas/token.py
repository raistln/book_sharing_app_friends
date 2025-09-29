"""
Esquemas relacionados con la autenticación y tokens JWT.
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Modelo para la respuesta de autenticación exitosa."""
    access_token: str = Field(
        ...,
        description="Token de acceso JWT para autenticar solicitudes",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token, siempre es 'bearer'",
        json_schema_extra={"example": "bearer"}
    )


class TokenData(BaseModel):
    """Modelo para los datos contenidos en el token JWT."""
    username: str | None = Field(
        default=None,
        description="Nombre de usuario del propietario del token",
        json_schema_extra={"example": "usuario_ejemplo"}
    )
    scopes: list[str] = Field(
        default_factory=list,
        description="Ámbitos de acceso del token",
        json_schema_extra={"example": ["me", "items"]}
    )
