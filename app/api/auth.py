"""
Endpoints de autenticación: registro, login, perfil actual
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, User as UserSchema
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_access_token,
    get_current_user,
)
from app.models.user import User
from app.utils.rate_limiter import auth_rate_limit
from app.utils.logger import log_endpoint_call, log_auth_attempt


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("book_sharing.auth")


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
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


@router.post("/login")
@auth_rate_limit()
@log_endpoint_call("/auth/login", "POST")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Login attempt username=%s from IP=%s", form_data.username, client_ip)
    
    # Validate username format to prevent SQL injection
    import re
    if not re.match(r'^[a-zA-Z0-9_.-]+$', form_data.username):
        log_auth_attempt(form_data.username, False, client_ip)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid username format")
    
    # Check for SQL injection patterns
    sql_patterns = [
        r"'.*'", r'".*"', r'--', r'/\*.*\*/',
        r'\bDROP\b', r'\bDELETE\b', r'\bUNION\b', r'\bSELECT\b',
        r'\bINSERT\b', r'\bUPDATE\b', r'\bCREATE\b', r'\bALTER\b'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, form_data.username, re.IGNORECASE):
            log_auth_attempt(form_data.username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid username format")
    
    try:
        user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
        if not user:
            log_auth_attempt(form_data.username, False, client_ip)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        
        access_token = create_user_access_token(user)
        log_auth_attempt(form_data.username, True, client_ip)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        log_auth_attempt(form_data.username, False, client_ip)
        logger.error(f"Login error for {form_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


# Alias para compatibilidad con tests que usan /auth/token
@router.post("/token")
@auth_rate_limit()
async def token_alias(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await login(request=request, form_data=form_data, db=db)


@router.get("/me", response_model=UserSchema)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


