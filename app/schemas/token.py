"""
Esquemas relacionados con la autenticación y tokens JWT.
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Modelo para la respuesta de autenticación exitosa."""
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="Token de acceso JWT para autenticar solicitudes"
    )
    token_type: str = Field(
        default="bearer",
        example="bearer",
        description="Tipo de token, siempre es 'bearer'"
    )


class TokenData(BaseModel):
    """Modelo para los datos contenidos en el token JWT."""
    username: str | None = Field(
        default=None,
        example="usuario_ejemplo",
        description="Nombre de usuario del propietario del token"
    )
    scopes: list[str] = Field(
        default_factory=list,
        example=["me", "items"],
        description="Ámbitos de acceso del token"
    )
