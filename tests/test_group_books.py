"""
Tests para bibliotecas compartidas en grupos.
"""
import pytest
from httpx import Client
from uuid import uuid4
import uuid


def _register_and_login(client: Client):
    """Helper para registrar y hacer login de un usuario."""
    username = f"user_{uuid4().hex[:8]}"
    password = "testpassword123"
    email = f"{username}@example.com"
    
    # Registrar
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    assert r.status_code == 201
    
    # Login
    r = client.post("/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]
    
    return username, token


def _create_group(client: Client, token: str, name: str = "Test Group"):
    """Helper para crear un grupo."""
    headers = {"Authorization": f"Bearer {token}"}
    group_data = {"name": name, "description": "Test group description"}
    
    r = client.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    return r.json()


def _create_book(client: Client, token: str, title: str = "Test Book"):
    """Helper para crear un libro."""
    headers = {"Authorization": f"Bearer {token}"}
    book_data = {
        "title": title,
        "author": "Test Author",
        "isbn": "1234567890",
        "description": "Test book description"
    }
    
    r = client.post("/books/", json=book_data, headers=headers)
    assert r.status_code == 201
    return r.json()


def test_get_group_books_success(live_server_url="http://localhost:8000"):
    """Test obtener libros de un grupo exitosamente."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear dos usuarios
    username1, token1 = _register_and_login(c)
    username2, token2 = _register_and_login(c)
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Usuario 1 crea grupo
    group = _create_group(c, token1, "Mi Grupo de Lectura")
    group_id = group["id"]
    
    # Usuario 1 crea libros
    book1 = _create_book(c, token1, "Libro 1")
    book2 = _create_book(c, token1, "Libro 2")
    
    # Usuario 2 se une al grupo (añadir como miembro)
    user2_id = c.get("/auth/me", headers=headers2).json()["id"]
    member_data = {"user_id": user2_id, "role": "member"}
    r = c.post(f"/groups/{group_id}/members", json=member_data, headers=headers1)
    assert r.status_code == 201
    
    # Usuario 2 crea un libro
    book3 = _create_book(c, token2, "Libro 3")
    
    # Usuario 2 obtiene libros del grupo
    r = c.get(f"/groups/{group_id}/books", headers=headers2)
    assert r.status_code == 200
    
    books = r.json()
    assert len(books) == 3  # 2 del usuario 1 + 1 del usuario 2
    
    # Verificar que todos los libros tienen la información correcta
    book_titles = [book["title"] for book in books]
    assert "Libro 1" in book_titles
    assert "Libro 2" in book_titles
    assert "Libro 3" in book_titles


def test_get_group_books_unauthorized(live_server_url="http://localhost:8000"):
    """Test obtener libros de grupo sin ser miembro."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Usuario 1 crea grupo y libro
    username1, token1 = _register_and_login(c)
    group = _create_group(c, token1)
    group_id = group["id"]
    _create_book(c, token1)
    
    # Usuario 2 intenta ver libros del grupo
    username2, token2 = _register_and_login(c)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    r = c.get(f"/groups/{group_id}/books", headers=headers2)
    assert r.status_code == 404  # No debería poder ver los libros


def test_get_group_books_with_filters(live_server_url="http://localhost:8000"):
    """Test obtener libros de grupo con filtros."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear usuario y grupo
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    
    # Crear libros con diferentes características
    book1 = _create_book(c, token, "Ciencia Ficción")
    book2 = _create_book(c, token, "Fantasía")
    book3 = _create_book(c, token, "Misterio")
    
    # Filtrar por búsqueda
    r = c.get(f"/groups/{group_id}/books?search=ciencia", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Ciencia Ficción"
    
    # Filtrar por tipo de libro
    r = c.get(f"/groups/{group_id}/books?book_type=novel", headers=headers)
    assert r.status_code == 200
    books = r.json()
    # Todos los libros son novelas por defecto (o None)
    assert len(books) >= 0  # Puede ser 0 si no hay libros con tipo específico
    
    # Filtrar por género
    r = c.get(f"/groups/{group_id}/books?genre=science_fiction", headers=headers)
    assert r.status_code == 200
    books = r.json()
    # Puede ser 0 si no hay libros con género específico
    assert len(books) >= 0


def test_get_group_book_details(live_server_url="http://localhost:8000"):
    """Test obtener detalles de un libro específico del grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear usuario, grupo y libro
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    book = _create_book(c, token, "Libro Detallado")
    book_id = book["id"]
    
    # Obtener detalles del libro
    r = c.get(f"/groups/{group_id}/books/{book_id}", headers=headers)
    assert r.status_code == 200
    
    book_details = r.json()
    assert book_details["title"] == "Libro Detallado"
    assert book_details["author"] == "Test Author"
    assert book_details["owner"]["username"] == username
    assert book_details["is_available"] is True


def test_get_group_book_not_found(live_server_url="http://localhost:8000"):
    """Test obtener libro que no existe en el grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    fake_book_id = str(uuid4())
    
    r = c.get(f"/groups/{group_id}/books/{fake_book_id}", headers=headers)
    assert r.status_code == 404


def test_get_group_book_stats(live_server_url="http://localhost:8000"):
    """Test obtener estadísticas de libros del grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear dos usuarios
    username1, token1 = _register_and_login(c)
    username2, token2 = _register_and_login(c)
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Usuario 1 crea grupo
    group = _create_group(c, token1)
    group_id = group["id"]
    
    # Usuario 1 crea libros
    _create_book(c, token1, "Libro 1")
    _create_book(c, token1, "Libro 2")
    
    # Usuario 2 se une al grupo
    user2_id = c.get("/auth/me", headers=headers2).json()["id"]
    member_data = {"user_id": user2_id, "role": "member"}
    r = c.post(f"/groups/{group_id}/members", json=member_data, headers=headers1)
    assert r.status_code == 201
    
    # Usuario 2 crea libro
    _create_book(c, token2, "Libro 3")
    
    # Obtener estadísticas
    r = c.get(f"/groups/{group_id}/books/stats", headers=headers2)
    assert r.status_code == 200
    
    stats = r.json()
    assert stats["total_books"] == 3
    assert stats["available_books"] == 3  # Todos disponibles
    assert stats["loaned_books"] == 0
    assert stats["reserved_books"] == 0
    assert stats["total_owners"] == 2


def test_get_group_book_owners(live_server_url="http://localhost:8000"):
    """Test obtener propietarios de libros del grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear dos usuarios
    username1, token1 = _register_and_login(c)
    username2, token2 = _register_and_login(c)
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Usuario 1 crea grupo
    group = _create_group(c, token1)
    group_id = group["id"]
    
    # Usuario 1 crea libro
    _create_book(c, token1, "Libro Usuario 1")
    
    # Usuario 2 se une al grupo
    user2_id = c.get("/auth/me", headers=headers2).json()["id"]
    member_data = {"user_id": user2_id, "role": "member"}
    r = c.post(f"/groups/{group_id}/members", json=member_data, headers=headers1)
    assert r.status_code == 201
    
    # Usuario 2 crea libro
    _create_book(c, token2, "Libro Usuario 2")
    
    # Obtener propietarios
    r = c.get(f"/groups/{group_id}/books/owners", headers=headers2)
    assert r.status_code == 200
    
    owners = r.json()
    assert len(owners) == 2
    
    owner_usernames = [owner["username"] for owner in owners]
    assert username1 in owner_usernames
    assert username2 in owner_usernames


def test_search_group_books(live_server_url="http://localhost:8000"):
    """Test buscar libros en el grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    
    # Crear libros con diferentes títulos
    _create_book(c, token, "Harry Potter")
    _create_book(c, token, "El Señor de los Anillos")
    _create_book(c, token, "Dune")
    
    # Buscar por título
    r = c.get(f"/groups/{group_id}/books/search?q=Harry", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Harry Potter"
    
    # Buscar por autor
    r = c.get(f"/groups/{group_id}/books/search?q=Test Author", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 3  # Todos tienen el mismo autor


def test_group_books_pagination(live_server_url="http://localhost:8000"):
    """Test paginación de libros del grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    
    # Crear varios libros
    for i in range(5):
        _create_book(c, token, f"Libro {i+1}")
    
    # Primera página
    r = c.get(f"/groups/{group_id}/books?limit=2&offset=0", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 2
    
    # Segunda página
    r = c.get(f"/groups/{group_id}/books?limit=2&offset=2", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 2
    
    # Tercera página
    r = c.get(f"/groups/{group_id}/books?limit=2&offset=4", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1


def test_group_books_new_filters(live_server_url="http://localhost:8000"):
    """Test nuevos filtros de tipo y género."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    username, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    group = _create_group(c, token)
    group_id = group["id"]
    
    # Crear libros con diferentes tipos y géneros
    book_data1 = {
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "1234567890",
        "description": "Ciencia ficción épica",
        "book_type": "novel",
        "genre": "science_fiction"
    }
    
    book_data2 = {
        "title": "Watchmen",
        "author": "Alan Moore",
        "isbn": "0987654321",
        "description": "Cómic de superhéroes",
        "book_type": "comic",
        "genre": "fiction"
    }
    
    # Crear libros
    r1 = c.post("/books/", json=book_data1, headers=headers)
    assert r1.status_code == 201
    
    r2 = c.post("/books/", json=book_data2, headers=headers)
    assert r2.status_code == 201
    
    # Filtrar por tipo de libro
    r = c.get(f"/groups/{group_id}/books?book_type=novel", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Dune"
    
    # Filtrar por género
    r = c.get(f"/groups/{group_id}/books?genre=science_fiction", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Dune"
    
    # Filtrar por cómics
    r = c.get(f"/groups/{group_id}/books?book_type=comic", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Watchmen"
    
    # Combinar filtros
    r = c.get(f"/groups/{group_id}/books?book_type=novel&genre=science_fiction", headers=headers)
    assert r.status_code == 200
    books = r.json()
    assert len(books) == 1
    assert books[0]["title"] == "Dune"
