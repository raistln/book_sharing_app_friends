"""
Endpoints de autenticación: registro, login, perfil actual
"""
from fastapi import APIRouter, Depends, HTTPException, status
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


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info("Register user username=%s email=%s", user_in.username, user_in.email)
    user = register_user(db=db, user_in=user_in)
    return user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info("Login attempt username=%s", form_data.username)
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas")
    access_token = create_user_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


# Alias para compatibilidad con tests que usan /auth/token
@router.post("/token")
def token_alias(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login(form_data=form_data, db=db)


@router.get("/me", response_model=UserSchema)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


