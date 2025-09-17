"""
Metadata endpoints for frontend support
"""
from fastapi import APIRouter, Request
from typing import List, Dict, Any
from app.utils.rate_limiter import api_rate_limit

router = APIRouter(prefix="/metadata", tags=["metadata"])

@router.get("/genres")
@api_rate_limit()
async def get_genres(request: Request) -> List[str]:
    """Get available book genres"""
    return [
        "Ficción",
        "No ficción", 
        "Ciencia",
        "Historia",
        "Biografía",
        "Técnico",
        "Romance",
        "Misterio",
        "Fantasía",
        "Ciencia ficción",
        "Terror",
        "Aventura",
        "Autoayuda",
        "Cocina",
        "Arte",
        "Filosofía",
        "Religión",
        "Política",
        "Economía",
        "Psicología"
    ]

@router.get("/book-types")
@api_rate_limit()
async def get_book_types(request: Request) -> List[str]:
    """Get available book types"""
    return ["physical", "digital"]

@router.get("/book-conditions")
@api_rate_limit()
async def get_book_conditions(request: Request) -> List[Dict[str, str]]:
    """Get available book conditions"""
    return [
        {"value": "excellent", "label": "Excelente"},
        {"value": "good", "label": "Bueno"},
        {"value": "fair", "label": "Regular"},
        {"value": "poor", "label": "Malo"}
    ]

@router.get("/loan-statuses")
@api_rate_limit()
async def get_loan_statuses(request: Request) -> List[Dict[str, str]]:
    """Get available loan statuses"""
    return [
        {"value": "pending", "label": "Pendiente"},
        {"value": "approved", "label": "Aprobado"},
        {"value": "rejected", "label": "Rechazado"},
        {"value": "active", "label": "Activo"},
        {"value": "returned", "label": "Devuelto"},
        {"value": "overdue", "label": "Vencido"}
    ]

@router.get("/languages")
@api_rate_limit()
async def get_languages(request: Request) -> List[Dict[str, str]]:
    """Get available languages"""
    return [
        {"code": "es", "name": "Español"},
        {"code": "en", "name": "English"},
        {"code": "fr", "name": "Français"},
        {"code": "de", "name": "Deutsch"},
        {"code": "it", "name": "Italiano"},
        {"code": "pt", "name": "Português"},
        {"code": "ca", "name": "Català"},
        {"code": "eu", "name": "Euskera"}
    ]

@router.get("/pagination-options")
@api_rate_limit()
async def get_pagination_options(request: Request) -> Dict[str, Any]:
    """Get pagination configuration options"""
    return {
        "default_page_size": 20,
        "available_page_sizes": [10, 20, 50, 100],
        "max_page_size": 100
    }

@router.get("/file-upload-limits")
@api_rate_limit()
async def get_file_upload_limits(request: Request) -> Dict[str, Any]:
    """Get file upload limitations"""
    return {
        "max_file_size_mb": 5,
        "allowed_image_types": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"],
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"]
    }
