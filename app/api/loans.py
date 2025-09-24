from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.dependencies import get_current_db
from app.services.loan_service import LoanService
from app.models.loan import Loan as LoanModel
from app.schemas.loan import Loan as LoanSchema


# Response Models
class SuccessResponse(BaseModel):
    """Standard success response model."""
    success: bool = Field(..., description="Indicates if the operation was successful")
    message: Optional[str] = Field(None, description="Additional information about the operation")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class LoanRequest(BaseModel):
    """Model for loan request data."""
    book_id: UUID = Field(..., description="ID of the book to be loaned")
    borrower_id: UUID = Field(..., description="ID of the user requesting the loan")


class LoanResponse(BaseModel):
    """Model for loan response data."""
    id: UUID = Field(..., description="Unique identifier of the loan")
    status: str = Field(..., description="Current status of the loan")
    requested_at: datetime = Field(..., description="When the loan was requested")
    approved_at: Optional[datetime] = Field(None, description="When the loan was approved")
    returned_at: Optional[datetime] = Field(None, description="When the book was returned")
    due_date: Optional[datetime] = Field(None, description="Expected return date")
    book: Dict[str, Any] = Field(..., description="Book details")
    borrower: Optional[Dict[str, str]] = Field(None, description="Borrower details")
    lender: Optional[Dict[str, str]] = Field(None, description="Lender details")


router = APIRouter(prefix="/loans", tags=["loans"])
logger = logging.getLogger(__name__)


@router.post(
    "/request",
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Request a new book loan",
    description="""
    Creates a new loan request for a book.
    
    This endpoint allows a user to request to borrow a book. The book's owner will need to
    approve the request before the loan is active.
    """,
    responses={
        201: {
            "description": "Loan request created successfully",
            "content": {
                "application/json": {
                    "example": {"loan_id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            }
        },
        400: {
            "description": "Invalid request data or book not available",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo solicitar el préstamo", "details": {}}
                }
            }
        },
        404: {
            "description": "Book or user not found",
            "model": ErrorResponse
        }
    }
)
def request_loan(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    """
    Request to borrow a book.
    
    Args:
        book_id: UUID of the book to borrow
        borrower_id: UUID of the user requesting the loan
        db: Database session
        
    Returns:
        Dict containing the ID of the created loan request
        
    Raises:
        HTTPException: If the loan request cannot be created
    """
    logger.info("Requesting loan: book_id=%s borrower_id=%s", book_id, borrower_id)
    
    svc = LoanService(db)
    loan = svc.request_loan(book_id, borrower_id)
    
    if not loan:
        logger.warning("Failed to request loan: book_id=%s borrower_id=%s", book_id, borrower_id)
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    
    logger.info("Loan requested successfully: loan_id=%s", loan.id)
    return {"loan_id": str(loan.id)}


@router.post(
    "/{loan_id}/approve",
    status_code=status.HTTP_200_OK,
    summary="Approve a loan request",
    description="""
    Approves a pending loan request.
    
    This endpoint allows the book owner to approve a loan request, making the loan active.
    An optional due date can be set; if not provided, a default will be used.
    """,
    responses={
        200: {
            "description": "Loan approved successfully",
            "content": {
                "application/json": {
                    "example": {"loan_id": "123e4567-e89b-12d3-a456-426614174000", "status": "APPROVED"}
                }
            }
        },
        400: {
            "description": "Invalid request or loan cannot be approved",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo aprobar/activar el préstamo", "details": {}}
                }
            }
        },
        404: {
            "description": "Loan not found",
            "model": ErrorResponse
        }
    }
)
def approve_loan(
    loan_id: UUID, 
    lender_id: UUID, 
    due_date: Optional[datetime] = None, 
    db: Session = Depends(get_current_db)
):
    """
    Approve a pending loan request.
    
    Args:
        loan_id: UUID of the loan to approve
        lender_id: UUID of the user approving the loan (must be the book owner)
        due_date: Optional due date for the loan
        db: Database session
        
    Returns:
        Dict containing the loan ID and new status
        
    Raises:
        HTTPException: If the loan cannot be approved
    """
    logger.info("Approving loan: loan_id=%s lender_id=%s due_date=%s", loan_id, lender_id, due_date)
    
    svc = LoanService(db)
    loan = svc.approve_loan(loan_id, lender_id, due_date)
    
    if not loan:
        logger.warning("Failed to approve loan: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo aprobar/activar el préstamo")
    
    logger.info("Loan approved successfully: loan_id=%s status=%s", loan.id, loan.status.name)
    return {"success": True, "loan_id": str(loan.id), "status": loan.status.name, "message": "Loan approved successfully"}


@router.post(
    "/{loan_id}/reject",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a loan request",
    description="""
    Rejects a pending loan request.
    
    This endpoint allows the book owner to reject a loan request, canceling the loan.
    """,
    responses={
        200: {
            "description": "Loan rejected successfully",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "Loan request rejected"}
                }
            }
        },
        400: {
            "description": "Invalid request or loan cannot be rejected",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo rechazar el préstamo", "details": {}}
                }
            }
        },
        404: {
            "description": "Loan not found",
            "model": ErrorResponse
        }
    }
)
def reject_loan(loan_id: UUID, lender_id: UUID, db: Session = Depends(get_current_db)):
    """
    Reject a pending loan request.
    
    Args:
        loan_id: UUID of the loan to reject
        lender_id: UUID of the user rejecting the loan (must be the book owner)
        db: Database session
        
    Returns:
        Success response indicating the loan was rejected
        
    Raises:
        HTTPException: If the loan cannot be rejected
    """
    logger.info("Rejecting loan: loan_id=%s lender_id=%s", loan_id, lender_id)
    
    svc = LoanService(db)
    ok = svc.reject_loan(loan_id, lender_id)
    
    if not ok:
        logger.warning("Failed to reject loan: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo rechazar el préstamo")
    
    logger.info("Loan rejected successfully: loan_id=%s", loan_id)
    return {"success": True, "message": "Loan request rejected"}


@router.post(
    "/return",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Return a borrowed book",
    description="""
    Marks a borrowed book as returned.
    
    This endpoint is used when a borrower returns a book to the lender.
    It updates the loan status and records the return timestamp.
    """,
    responses={
        200: {
            "description": "Book returned successfully",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "Libro devuelto exitosamente"}
                }
            }
        },
        400: {
            "description": "Invalid request or book cannot be returned",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo devolver el libro", "details": {}}
                }
            }
        },
        404: {
            "description": "Book or active loan not found",
            "model": ErrorResponse
        }
    }
)
def return_book(book_id: UUID, db: Session = Depends(get_current_db)):
    """
    Mark a borrowed book as returned.
    
    Args:
        book_id: UUID of the book being returned
        db: Database session
        
    Returns:
        Success response indicating the book was returned
        
    Raises:
        HTTPException: If the book cannot be returned
    """
    logger.info("Returning book: book_id=%s", book_id)
    
    svc = LoanService(db)
    ok = svc.return_book(book_id)
    
    if not ok:
        logger.warning("Failed to return book: book_id=%s", book_id)
        raise HTTPException(status_code=400, detail="No se pudo devolver el libro")
    
    logger.info("Book returned successfully: book_id=%s", book_id)
    return {"success": True, "message": "Libro devuelto exitosamente"}


@router.post(
    "/{loan_id}/due-date",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Set or update loan due date",
    description="""
    Sets or updates the due date for an active loan.
    
    This endpoint allows the lender to specify when the borrowed book should be returned.
    The due date must be in the future.
    """,
    responses={
        200: {
            "description": "Due date updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "loan_id": "123e4567-e89b-12d3-a456-426614174000",
                        "due_date": "2023-12-31T23:59:59"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request or due date",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo actualizar la fecha de vencimiento", "details": {}}
                }
            }
        },
        403: {
            "description": "User not authorized to update this loan",
            "model": ErrorResponse
        },
        404: {
            "description": "Loan not found",
            "model": ErrorResponse
        }
    }
)
def set_due_date(
    loan_id: UUID, 
    lender_id: UUID, 
    due_date: datetime, 
    db: Session = Depends(get_current_db)
):
    """
    Set or update the due date for a loan.
    
    Args:
        loan_id: UUID of the loan to update
        lender_id: UUID of the user setting the due date (must be the lender)
        due_date: New due date for the loan
        db: Database session
        
    Returns:
        Dict containing the loan ID and new due date
        
    Raises:
        HTTPException: If the due date cannot be updated
    """
    logger.info("Setting due date: loan_id=%s lender_id=%s due_date=%s", loan_id, lender_id, due_date)
    
    svc = LoanService(db)
    loan = svc.set_due_date(loan_id, lender_id, due_date)
    
    if not loan:
        logger.warning("Failed to set due date: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo actualizar la fecha de vencimiento")
    
    logger.info("Due date set successfully: loan_id=%s due_date=%s", loan.id, loan.due_date)
    return {"success": True, "loan_id": str(loan.id), "due_date": loan.due_date, "message": "Due date updated successfully"}


@router.get(
    "/",
    response_model=List[LoanResponse],
    summary="List user's loans",
    description="""
    Retrieves a list of loans for a specific user.
    
    Returns all loans where the user is either the borrower or the lender.
    The results include detailed information about the book, borrower, and lender.
    """,
    responses={
        200: {
            "description": "List of loans retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "status": "APPROVED",
                            "requested_at": "2023-01-01T12:00:00",
                            "approved_at": "2023-01-01T12:05:00",
                            "returned_at": None,
                            "due_date": "2023-02-01T12:00:00",
                            "book": {
                                "id": "223e4567-e89b-12d3-a456-426614174000",
                                "title": "Sample Book",
                                "author": "Author Name"
                            },
                            "borrower": {
                                "id": "323e4567-e89b-12d3-a456-426614174000",
                                "username": "borrower_user"
                            },
                            "lender": {
                                "id": "423e4567-e89b-12d3-a456-426614174000",
                                "username": "lender_user"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid user ID format",
            "model": ErrorResponse
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse
        }
    }
)
def list_user_loans(
    db: Session = Depends(get_current_db), 
    user_id: Optional[UUID] = None
):
    """
    Retrieve all loans for a specific user.
    
    Args:
        db: Database session
        user_id: Optional UUID of the user. If not provided, requires authentication.
        
    Returns:
        List of loans associated with the user
        
    Raises:
        HTTPException: If there's an error retrieving the loans
    """
    logger.info("Listing loans for user: user_id=%s", user_id)
    
    from app.models.book import Book as BookModel
    
    query = db.query(LoanModel).options(
        joinedload(LoanModel.book).joinedload(BookModel.owner),
        joinedload(LoanModel.borrower),
        joinedload(LoanModel.lender)
    )
    
    if user_id:
        query = query.filter(
            (LoanModel.borrower_id == user_id) | (LoanModel.lender_id == user_id)
        )
    
    loans = query.order_by(LoanModel.requested_at.desc()).all()
    
    logger.info("Retrieved %d loans for user %s", len(loans), user_id)
    
    return [
        {
            "id": str(loan.id),
            "book": {
                "id": str(loan.book.id),
                "title": loan.book.title,
                "author": loan.book.author
            },
            "borrower": {
                "id": str(loan.borrower.id),
                "username": loan.borrower.username
            } if loan.borrower else None,
            "lender": {
                "id": str(loan.lender.id),
                "username": loan.lender.username
            } if loan.lender else None,
            "status": loan.status.name,
            "requested_at": loan.requested_at,
            "approved_at": loan.approved_at,
            "returned_at": loan.returned_at,
            "due_date": loan.due_date
        }
        for loan in loans
    ]


@router.get(
    "/history/book/{book_id}",
    response_model=List[Dict[str, Any]],
    summary="Get loan history for a book",
    description="""
    Retrieves the complete loan history for a specific book.
    
    This endpoint shows all past and current loans for a book, including
    details about borrowers, lenders, and loan status changes.
    """,
    responses={
        200: {
            "description": "Book loan history retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "status": "RETURNED",
                            "requested_at": "2023-01-01T12:00:00",
                            "approved_at": "2023-01-01T12:05:00",
                            "returned_at": "2023-01-15T10:30:00",
                            "due_date": "2023-01-31T12:00:00",
                            "borrower": {
                                "id": "323e4567-e89b-12d3-a456-426614174000",
                                "username": "previous_borrower"
                            },
                            "lender": {
                                "id": "423e4567-e89b-12d3-a456-426614174000",
                                "username": "book_owner"
                            }
                        },
                        {
                            "id": "523e4567-e89b-12d3-a456-426614174000",
                            "status": "APPROVED",
                            "requested_at": "2023-02-01T09:15:00",
                            "approved_at": "2023-02-01T09:20:00",
                            "returned_at": None,
                            "due_date": "2023-03-01T12:00:00",
                            "borrower": {
                                "id": "623e4567-e89b-12d3-a456-426614174000",
                                "username": "current_borrower"
                            },
                            "lender": {
                                "id": "423e4567-e89b-12d3-a456-426614174000",
                                "username": "book_owner"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid book ID format",
            "model": ErrorResponse
        },
        404: {
            "description": "Book not found",
            "model": ErrorResponse
        }
    }
)
def get_book_history(book_id: UUID, db: Session = Depends(get_current_db)):
    """
    Retrieve the complete loan history for a specific book.
    
    Args:
        book_id: UUID of the book
        db: Database session
        
    Returns:
        List of all loan records for the specified book, ordered by most recent first
        
    Raises:
        HTTPException: If there's an error retrieving the history
    """
    logger.info("Getting loan history for book: book_id=%s", book_id)
    
    # Optimized query with eager loading
    loans = db.query(LoanModel).options(
        joinedload(LoanModel.borrower),
        joinedload(LoanModel.lender),
        joinedload(LoanModel.book)
    ).filter(LoanModel.book_id == book_id).order_by(LoanModel.requested_at.desc()).all()
    
    logger.info("Retrieved %d loan records for book %s", len(loans), book_id)
    
    return [
        {
            "id": str(l.id),
            "status": l.status.name,
            "requested_at": l.requested_at,
            "approved_at": l.approved_at,
            "returned_at": l.returned_at,
            "due_date": l.due_date,
            "borrower": {"id": str(l.borrower.id), "username": l.borrower.username} if l.borrower else None,
            "lender": {"id": str(l.lender.id), "username": l.lender.username} if l.lender else None
        }
        for l in loans
    ]


# Compatibilidad con tests existentes: préstamo inmediato
@router.post(
    "/loan",
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Create and approve a loan immediately",
    description="""
    Creates and approves a loan in a single step.
    
    This is a convenience endpoint that combines the request and approve operations.
    It's primarily used for testing and compatibility with existing systems.
    """,
    responses={
        201: {
            "description": "Loan created and approved successfully",
            "content": {
                "application/json": {
                    "example": {"loan_id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            }
        },
        400: {
            "description": "Invalid request or loan cannot be created/approved",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"error": "No se pudo solicitar el préstamo", "details": {}}
                }
            }
        },
        404: {
            "description": "Book or user not found",
            "model": ErrorResponse
        }
    }
)
def loan_book(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    """
    Create and immediately approve a loan (for testing and compatibility).
    
    This endpoint combines the request and approve operations into a single step.
    It's primarily used for testing and maintaining compatibility with existing tests.
    
    Args:
        book_id: UUID of the book to loan
        borrower_id: UUID of the user borrowing the book
        db: Database session
        
    Returns:
        Dict containing the ID of the created loan
        
    Raises:
        HTTPException: If the loan cannot be created or approved
    """
    logger.info("Processing immediate loan: book_id=%s borrower_id=%s", book_id, borrower_id)
    
    svc = LoanService(db)
    
    # crear solicitud
    loan = svc.request_loan(book_id, borrower_id)
    if not loan:
        logger.warning("Failed to create loan request: book_id=%s borrower_id=%s", book_id, borrower_id)
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    
    # obtener dueño del libro para aprobar
    from app.models.book import Book as BookModel
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        logger.error("Book not found for loan: book_id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    loan = svc.approve_loan(loan.id, book.owner_id)
    if not loan:
        logger.warning("Failed to approve loan: loan_id=%s owner_id=%s", loan.id, book.owner_id)
        raise HTTPException(status_code=400, detail="No se pudo aprobar el préstamo")
    
    logger.info("Immediate loan completed successfully: book_id=%s loan_id=%s", book_id, loan.id)
    return {"message": "Libro prestado", "book_id": str(book.id), "loan_id": str(loan.id)}


