"""
Consistent pagination utilities for list endpoints
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Query
from sqlalchemy import func
from math import ceil

from pydantic import field_validator

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    per_page: int = 20
    
    @field_validator('page')
    def validate_page(cls, v):
        """Ensure page is at least 1"""
        return max(1, v)
    
    @field_validator('per_page')
    def validate_per_page(cls, v):
        """Ensure per_page is between 1 and 100"""
        return max(1, min(v, 100))

class PaginatedResponse(BaseModel):
    """Standard paginated response format"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

def paginate_query(
    query: Query, 
    page: int = 1, 
    per_page: int = 20,
    max_per_page: int = 100
) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-based)
        per_page: Items per page
        max_per_page: Maximum items per page allowed
        
    Returns:
        PaginatedResponse: Paginated results
    """
    # Validate and sanitize parameters
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    
    # Get total count
    total = query.count()
    
    # Calculate pagination info
    total_pages = ceil(total / per_page) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None
    
    # Get items for current page
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=next_page,
        prev_page=prev_page
    )

def paginate_list(
    items: List[Any], 
    page: int = 1, 
    per_page: int = 20,
    max_per_page: int = 100
) -> PaginatedResponse:
    """
    Paginate a Python list
    
    Args:
        items: List of items to paginate
        page: Page number (1-based)
        per_page: Items per page
        max_per_page: Maximum items per page allowed
        
    Returns:
        PaginatedResponse: Paginated results
    """
    # Validate and sanitize parameters
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    
    total = len(items)
    total_pages = ceil(total / per_page) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get items for current page
    page_items = items[start_idx:end_idx]
    
    return PaginatedResponse(
        items=page_items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=next_page,
        prev_page=prev_page
    )

def create_pagination_metadata(
    total: int,
    page: int,
    per_page: int
) -> Dict[str, Any]:
    """
    Create pagination metadata dictionary
    
    Args:
        total: Total number of items
        page: Current page number
        per_page: Items per page
        
    Returns:
        Dict: Pagination metadata
    """
    total_pages = ceil(total / per_page) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None
    }
