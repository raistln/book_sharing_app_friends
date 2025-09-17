"""
Schemas Pydantic para Usuario
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    """Schema base para usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username to prevent SQL injection and ensure safe characters"""
        # Username must start with a letter
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Username must start with a letter and can only contain letters, numbers, underscores, and hyphens')
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"'.*'",  # Single quotes
            r'".*"',  # Double quotes
            r'--',    # SQL comments
            r'/\*.*\*/',  # Multi-line comments
            r'\bDROP\b', r'\bDELETE\b', r'\bUNION\b', r'\bSELECT\b',
            r'\bINSERT\b', r'\bUPDATE\b', r'\bCREATE\b', r'\bALTER\b'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Username contains invalid characters')
        
        return v


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema para usuario en base de datos"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class User(UserInDB):
    """Schema para respuesta de usuario (sin datos sensibles)"""
    pass


class UserBasic(BaseModel):
    """Schema básico para usuario (solo información esencial)"""
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class UserPasswordChange(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
