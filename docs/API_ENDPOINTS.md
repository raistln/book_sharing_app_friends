# API Endpoints Reference

This document lists all available API endpoints organized by their source files.

## Authentication (`app/api/auth.py`)
User registration, login, and account management
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /auth/me`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /auth/verify-email`
- `POST /auth/resend-verification`

## Books (`app/api/books.py`)
Manage book listings, including creating, reading, updating, and deleting books
- `GET /books/`
- `POST /books/`
- `GET /books/{book_id}`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`
- `GET /users/me/books`
- `GET /users/{user_id}/books`

## Search (`app/api/search_enhanced.py`)
Advanced search functionality for books, users, and groups with filters
- `GET /search/books`
- `GET /search/users`
- `GET /search/groups`
- `GET /search/suggestions`

## Users (`app/api/users.py`)
User profile management and favorite books
- `GET /users/`
- `GET /users/me`
- `PUT /users/me`
- `DELETE /users/me`
- `GET /users/{user_id}`
- `GET /users/me/favorites`
- `POST /users/me/favorites/{book_id}`
- `DELETE /users/me/favorites/{book_id}`

## Loans (`app/api/loans.py`)
Handle book lending and borrowing between users
- `GET /loans/`
- `POST /loans/`
- `GET /loans/{loan_id}`
- `PUT /loans/{loan_id}`
- `DELETE /loans/{loan_id}`
- `GET /users/me/loans`
- `GET /users/me/borrowed`
- `POST /loans/{loan_id}/return`
- `POST /loans/{loan_id}/renew`

## Groups (`app/api/groups.py`)
Manage user groups and group membership
- `GET /groups/`
- `POST /groups/`
- `GET /groups/{group_id}`
- `PUT /groups/{group_id}`
- `DELETE /groups/{group_id}`
- `GET /groups/{group_id}/members`
- `POST /groups/{group_id}/join`
- `POST /groups/{group_id}/leave`
- `POST /groups/{group_id}/members/{user_id}`
- `DELETE /groups/{group_id}/members/{user_id}`

## Group Books (`app/api/group_books.py`)
Manage book collections within groups
- `GET /groups/{group_id}/books`
- `POST /groups/{group_id}/books`
- `GET /groups/{group_id}/books/{book_id}`
- `PUT /groups/{group_id}/books/{book_id}`
- `DELETE /groups/{group_id}/books/{book_id}`

## Reviews (`app/api/reviews.py`)
Book reviews and ratings management
- `GET /books/{book_id}/reviews`
- `POST /books/{book_id}/reviews`
- `GET /reviews/{review_id}`
- `PUT /reviews/{review_id}`
- `DELETE /reviews/{review_id}`
- `POST /reviews/{review_id}/like`
- `DELETE /reviews/{review_id}/like`

## Chat (`app/api/chat.py`)
Real-time messaging between users
- `GET /chat/conversations`
- `POST /chat/conversations`
- `GET /chat/conversations/{conversation_id}`
- `GET /chat/conversations/{conversation_id}/messages`
- `POST /chat/conversations/{conversation_id}/messages`
- `GET /chat/conversations/with/{user_id}`

## Scan (`app/api/scan.py`)
Book scanning using ISBN or image recognition
- `POST /scan/isbn`
- `POST /scan/upload`
- `GET /scan/history`

## Metadata (`app/api/metadata.py`)
Reference data for the application (genres, languages, etc.)
- `GET /metadata/genres`
- `GET /metadata/languages`
- `GET /metadata/conditions`
- `GET /metadata/book-types`

## Health (`app/api/health.py`)
System health checks and monitoring
- `GET /health`
- `GET /health/db`
- `GET /health/redis`
- `GET /health/version`
   

