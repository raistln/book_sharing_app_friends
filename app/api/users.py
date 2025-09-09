"""
Endpoints básicos de usuario: perfil propio
"""
from fastapi import APIRouter, Depends

from app.schemas.user import User as UserSchema
from app.models.user import User
from app.services.auth_service import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def read_own_profile(current_user: User = Depends(get_current_user)):
    return current_user


