"""
Secure file validation utilities
"""
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import logging
from typing import Set

# Optional import for python-magic
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

logger = logging.getLogger(__name__)

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
ALLOWED_MIME_TYPES: Set[str] = {
    'image/jpeg', 'image/png', 'image/webp', 
    'image/gif', 'image/bmp'
}

# File size limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MIN_FILE_SIZE = 1024  # 1KB

async def validate_image_file(file: UploadFile) -> UploadFile:
    """
    Comprehensive image file validation
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        UploadFile: The validated file
        
    Raises:
        HTTPException: If validation fails
    """
    if not file.filename:
        raise HTTPException(
            status_code=400, 
            detail="Nombre de archivo requerido"
        )
    
    # 1. Validate file extension
    file_extension = '.' + file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 2. Read file contents
    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Error reading file {file.filename}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error al leer el archivo"
        )
    
    # 3. Validate file size
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    if file_size < MIN_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Archivo demasiado pequeño"
        )
    
    # 4. Validate MIME type using python-magic (if available)
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_buffer(contents, mime=True)
            if mime_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo MIME no permitido: {mime_type}"
                )
        except Exception as e:
            logger.warning(f"MIME type validation failed: {e}")
    else:
        logger.warning("python-magic not available, skipping MIME type validation")
    
    # 5. Validate that it's actually a valid image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
        
        # Additional checks
        if image.format.lower() not in ['jpeg', 'png', 'webp', 'gif', 'bmp']:
            raise HTTPException(
                status_code=400,
                detail="Formato de imagen no válido"
            )
        
        # Check image dimensions (reasonable limits)
        if hasattr(image, 'size'):
            width, height = image.size
            if width > 4000 or height > 4000:
                raise HTTPException(
                    status_code=400,
                    detail="Dimensiones de imagen demasiado grandes (máximo 4000x4000)"
                )
            if width < 10 or height < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Dimensiones de imagen demasiado pequeñas"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image validation failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida"
        )
    
    # 6. Reset file pointer for further processing
    await file.seek(0)
    
    logger.info(f"File validation successful for {file.filename} ({file_size} bytes)")
    return file

async def validate_document_file(file: UploadFile) -> UploadFile:
    """
    Validate document files (for future use)
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        UploadFile: The validated file
    """
    # Placeholder for document validation
    # Could be extended for PDF, TXT files etc.
    return file

def get_safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing potentially dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    import re
    import uuid
    
    # Remove path separators and dangerous characters
    safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Ensure filename is not too long
    if len(safe_filename) > 100:
        name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
        safe_filename = f"{name[:50]}_{uuid.uuid4().hex[:8]}.{ext}" if ext else f"{name[:50]}_{uuid.uuid4().hex[:8]}"
    
    return safe_filename
