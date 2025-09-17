"""
Enhanced search functionality with filtering and optimization
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app.database import get_db
from app.models.book import Book
from app.utils.pagination import paginate_query, PaginationParams
from app.utils.rate_limiter import search_rate_limit
from app.utils.logger import log_endpoint_call
import logging

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger("book_sharing.search")

@router.get("/books")
@search_rate_limit()
@log_endpoint_call("/search/books", "GET")
async def search_books(
    request: Request,
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    book_type: Optional[str] = Query(None, description="Filter by book type (physical/digital)"),
    language: Optional[str] = Query(None, description="Filter by language"),
    available_only: bool = Query(False, description="Show only available books"),
    condition: Optional[str] = Query(None, description="Filter by book condition"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    sort_by: str = Query("relevance", description="Sort by: relevance, title, author, created_at, rating"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    db: Session = Depends(get_db)
):
    """
    Enhanced book search with multiple filters and sorting options
    """
    # Base query - only non-deleted books
    query = db.query(Book).filter(Book.is_deleted == False)
    
    # Text search in title, author, description, and ISBN
    if q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.description.ilike(search_term),
                Book.isbn.ilike(search_term)
            )
        )
    
    # Apply filters
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    
    if book_type:
        query = query.filter(Book.book_type == book_type)
    
    if language:
        query = query.filter(Book.language == language)
    
    if available_only:
        query = query.filter(Book.status == "available")
    
    if condition:
        query = query.filter(Book.condition == condition)
    
    if min_rating is not None:
        query = query.filter(Book.rating >= min_rating)
    
    # Apply sorting
    if sort_by == "title":
        order_field = Book.title
    elif sort_by == "author":
        order_field = Book.author
    elif sort_by == "created_at":
        order_field = Book.created_at
    elif sort_by == "rating":
        order_field = Book.rating
    else:  # relevance or default
        order_field = Book.created_at  # Default to newest first
    
    if sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # Log search parameters
    logger.info(f"Book search: query='{q}', filters={{'genre': {genre}, 'type': {book_type}, 'available_only': {available_only}}}")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get("/users")
@search_rate_limit()
@log_endpoint_call("/search/users", "GET")
async def search_users(
    request: Request,
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search users by username or email
    """
    from app.models.user import User
    
    # Base query - only active users
    query = db.query(User).filter(User.is_active == True)
    
    # Text search in username and email
    if q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Order by username
    query = query.order_by(User.username.asc())
    
    logger.info(f"User search: query='{q}'")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get("/groups")
@search_rate_limit()
@log_endpoint_call("/search/groups", "GET")
async def search_groups(
    request: Request,
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    public_only: bool = Query(False, description="Show only public groups"),
    db: Session = Depends(get_db)
):
    """
    Search groups by name or description
    """
    from app.models.group import Group
    
    # Base query
    query = db.query(Group)
    
    # Filter public groups if requested
    if public_only:
        query = query.filter(Group.is_public == True)
    
    # Text search in name and description
    if q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Group.name.ilike(search_term),
                Group.description.ilike(search_term)
            )
        )
    
    # Order by name
    query = query.order_by(Group.name.asc())
    
    logger.info(f"Group search: query='{q}', public_only={public_only}")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get("/suggestions")
@search_rate_limit()
@log_endpoint_call("/search/suggestions", "GET")
async def get_search_suggestions(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    """
    suggestions = {
        "books": [],
        "authors": [],
        "genres": []
    }
    
    if len(q.strip()) < 2:
        return suggestions
    
    search_term = f"%{q.strip()}%"
    
    # Book title suggestions
    book_titles = db.query(Book.title).filter(
        and_(
            Book.title.ilike(search_term),
            Book.is_deleted == False
        )
    ).distinct().limit(limit).all()
    
    suggestions["books"] = [title[0] for title in book_titles]
    
    # Author suggestions
    authors = db.query(Book.author).filter(
        and_(
            Book.author.ilike(search_term),
            Book.is_deleted == False
        )
    ).distinct().limit(limit).all()
    
    suggestions["authors"] = [author[0] for author in authors if author[0]]
    
    # Genre suggestions (from a predefined list)
    all_genres = [
        "Ficción", "No ficción", "Ciencia", "Historia", "Biografía",
        "Técnico", "Romance", "Misterio", "Fantasía", "Ciencia ficción"
    ]
    
    suggestions["genres"] = [
        genre for genre in all_genres 
        if q.lower() in genre.lower()
    ][:limit]
    
    return suggestions
