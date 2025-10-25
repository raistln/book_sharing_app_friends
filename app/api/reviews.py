"""
API Endpoints para Reviews (Reseñas)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from uuid import UUID
from typing import List, Optional
import logging

from app.dependencies import get_current_db
from app.services.auth_service import get_current_user
from app.models.review import Review as ReviewModel
from app.models.user import User
from app.models.book import Book
from app.schemas.review import ReviewResponse, ReviewCreate, ReviewUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[ReviewResponse])
def list_reviews(
    book_id: Optional[UUID] = Query(None, description="Filtrar por ID de libro"),
    user_id: Optional[UUID] = Query(None, description="Filtrar por ID de usuario"),
    group_id: Optional[UUID] = Query(None, description="Filtrar por ID de grupo"),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    offset: int = Query(0, ge=0, description="Número de resultados a saltar"),
    db: Session = Depends(get_current_db)
):
    """Listar reseñas con filtros opcionales y paginación."""
    logger.info("Listing reviews with filters: book_id=%s, user_id=%s, group_id=%s", book_id, user_id, group_id)

    query = db.query(ReviewModel).options(
        joinedload(ReviewModel.book),
        joinedload(ReviewModel.user),
        joinedload(ReviewModel.group)
    )

    if book_id:
        query = query.filter(ReviewModel.book_id == book_id)
    if user_id:
        query = query.filter(ReviewModel.user_id == user_id)
    if group_id:
        query = query.filter(ReviewModel.group_id == group_id)

    reviews = query.order_by(desc(ReviewModel.created_at)).offset(offset).limit(limit).all()

    # Enriquecer respuesta con datos relacionados
    enriched_reviews = []
    for review in reviews:
        enriched_review = ReviewResponse.model_validate(review)
        enriched_review.book_title = review.book.title if review.book else None
        enriched_review.user_username = review.user.username if review.user else None
        enriched_review.group_name = review.group.name if review.group else None
        enriched_reviews.append(enriched_review)

    logger.info("Retrieved %d reviews", len(enriched_reviews))
    return enriched_reviews


@router.get("/my-reviews", response_model=List[ReviewResponse])
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
):
    """Obtener todas las reseñas del usuario autenticado."""
    logger.info("Getting my reviews for user_id=%s", current_user.id)

    reviews = db.query(ReviewModel).options(
        joinedload(ReviewModel.book),
        joinedload(ReviewModel.user),
        joinedload(ReviewModel.group)
    ).filter(ReviewModel.user_id == current_user.id).all()

    # Enriquecer respuestas
    enriched_reviews = []
    for review in reviews:
        enriched_review = ReviewResponse.model_validate(review)
        enriched_review.book_title = review.book.title if review.book else None
        enriched_review.user_username = current_user.username
        if review.group:
            enriched_review.group_name = review.group.name
        enriched_reviews.append(enriched_review)

    logger.info("Retrieved %d reviews for user", len(enriched_reviews))
    return enriched_reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: UUID, db: Session = Depends(get_current_db)):
    """Obtener una reseña por ID."""
    logger.info("Getting review: id=%s", review_id)

    review = db.query(ReviewModel).options(
        joinedload(ReviewModel.book),
        joinedload(ReviewModel.user),
        joinedload(ReviewModel.group)
    ).filter(ReviewModel.id == review_id).first()

    if not review:
        logger.warning("Review not found: id=%s", review_id)
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    # Enriquecer respuesta
    enriched_review = ReviewResponse.model_validate(review)
    enriched_review.book_title = review.book.title if review.book else None
    enriched_review.user_username = review.user.username if review.user else None
    enriched_review.group_name = review.group.name if review.group else None

    return enriched_review


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
):
    """Crear una nueva reseña para un libro."""
    logger.info("Creating review for book_id=%s by user_id=%s", review_data.book_id, current_user.id)

    # Verificar que el libro existe
    book = db.query(Book).filter(Book.id == review_data.book_id).first()
    if not book:
        logger.warning("Book not found: id=%s", review_data.book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # Verificar que el usuario no haya reseñado ya este libro
    existing_review = db.query(ReviewModel).filter(
        and_(
            ReviewModel.book_id == review_data.book_id,
            ReviewModel.user_id == current_user.id
        )
    ).first()

    if existing_review:
        logger.warning("User already reviewed this book: book_id=%s, user_id=%s", review_data.book_id, current_user.id)
        raise HTTPException(
            status_code=400,
            detail="Ya has reseñado este libro. Puedes actualizar tu reseña existente."
        )

    # Crear la reseña
    new_review = ReviewModel(
        rating=review_data.rating,
        comment=review_data.comment,
        book_id=review_data.book_id,
        user_id=current_user.id,
        group_id=review_data.group_id
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    logger.info("Review created successfully: id=%s", new_review.id)

    # Enriquecer respuesta
    enriched_review = ReviewResponse.model_validate(new_review)
    enriched_review.book_title = book.title
    enriched_review.user_username = current_user.username
    if review_data.group_id:
        from app.models.group import Group
        group = db.query(Group).filter(Group.id == review_data.group_id).first()
        if group:
            enriched_review.group_name = group.name

    return enriched_review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
):
    """Actualizar una reseña existente."""
    logger.info("Updating review: id=%s by user_id=%s", review_id, current_user.id)

    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        logger.warning("Review not found: id=%s", review_id)
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    # Verificar que el usuario es el autor de la reseña
    if review.user_id != current_user.id:
        logger.warning("User not authorized to update review: review_id=%s, user_id=%s", review_id, current_user.id)
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar esta reseña"
        )

    # Actualizar campos
    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.comment is not None:
        review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    logger.info("Review updated successfully: id=%s", review_id)

    # Enriquecer respuesta
    enriched_review = ReviewResponse.model_validate(review)
    enriched_review.book_title = review.book.title if review.book else None
    enriched_review.user_username = current_user.username
    enriched_review.group_name = review.group.name if review.group else None

    return enriched_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
):
    """Eliminar una reseña."""
    logger.info("Deleting review: id=%s by user_id=%s", review_id, current_user.id)

    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        logger.warning("Review not found: id=%s", review_id)
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    # Verificar que el usuario es el autor de la reseña
    if review.user_id != current_user.id:
        logger.warning("User not authorized to delete review: review_id=%s, user_id=%s", review_id, current_user.id)
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar esta reseña"
        )

    db.delete(review)
    db.commit()

    logger.info("Review deleted successfully: id=%s", review_id)
    return None
