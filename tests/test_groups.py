"""
Tests para el sistema de grupos e invitaciones.
"""
import pytest
import time
from httpx import Client
from uuid import uuid4
import uuid


def _register_and_login(client: Client):
    """Helper para registrar y hacer login de un usuario."""
    time.sleep(1)  # Add delay to prevent rate limiting
    username = f"user_{uuid4().hex[:8]}"
    password = "Testpassword123"  # Must have uppercase, lowercase, and digit
    email = f"{username}@example.com"
    
    # Registrar
    r = client.post("/auth/register", json={
        "username": username, 
        "password": password, 
        "email": email,
        "full_name": "Test User"
    })
    assert r.status_code == 201, f"Registration failed: {r.text}"
    
    # Login
    r = client.post("/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]
    
    return username, token


def test_create_group_success(live_server_url="http://localhost:8000"):
    """Test crear grupo exitosamente."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {
        "name": "Mi Grupo de Lectura",
        "description": "Grupo para compartir libros de ciencia ficción"
    }
    
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    
    group = r.json()
    assert group["name"] == group_data["name"]
    assert group["description"] == group_data["description"]
    assert group["created_by"] is not None
    assert len(group["members"]) == 1  # Solo el creador
    assert group["members"][0]["role"] == "admin"


def test_create_group_unauthorized(live_server_url="http://localhost:8000"):
    """Test crear grupo sin autenticación."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    group_data = {
        "name": "Mi Grupo",
        "description": "Descripción"
    }
    
    r = c.post("/groups/", json=group_data)
    assert r.status_code == 401


def test_get_user_groups(live_server_url="http://localhost:8000"):
    """Test obtener grupos del usuario."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear varios grupos
    groups_data = [
        {"name": "Grupo 1", "description": "Descripción 1"},
        {"name": "Grupo 2", "description": "Descripción 2"}
    ]
    
    created_groups = []
    for group_data in groups_data:
        r = c.post("/groups/", json=group_data, headers=headers)
        assert r.status_code == 201
        created_groups.append(r.json())
    
    # Obtener grupos del usuario
    r = c.get("/groups/", headers=headers)
    assert r.status_code == 200
    
    groups = r.json()
    assert len(groups) == 2
    
    for group in groups:
        assert group["name"] in ["Grupo 1", "Grupo 2"]
        assert group["member_count"] == 1
        assert group["is_admin"] is True


def test_get_group_details(live_server_url="http://localhost:8000"):
    """Test obtener detalles de un grupo específico."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {"name": "Mi Grupo", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Obtener detalles del grupo
    r = c.get(f"/groups/{group_id}", headers=headers)
    assert r.status_code == 200
    
    group = r.json()
    assert group["name"] == group_data["name"]
    assert group["description"] == group_data["description"]
    assert group["id"] == group_id


def test_get_group_not_found(live_server_url="http://localhost:8000"):
    """Test obtener grupo que no existe."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = str(uuid4())
    
    r = c.get(f"/groups/{fake_id}", headers=headers)
    assert r.status_code == 404


def test_update_group_success(live_server_url="http://localhost:8000"):
    """Test actualizar grupo exitosamente."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {"name": "Grupo Original", "description": "Descripción original"}
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Actualizar grupo
    update_data = {
        "name": "Grupo Actualizado",
        "description": "Descripción actualizada"
    }
    r = c.put(f"/groups/{group_id}", json=update_data, headers=headers)
    assert r.status_code == 200
    
    group = r.json()
    assert group["name"] == update_data["name"]
    assert group["description"] == update_data["description"]


def test_delete_group_success(live_server_url="http://localhost:8000"):
    """Test eliminar grupo exitosamente."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {"name": "Grupo a Eliminar", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Eliminar grupo
    r = c.delete(f"/groups/{group_id}", headers=headers)
    assert r.status_code == 204
    
    # Verificar que el grupo fue eliminado
    r = c.get(f"/groups/{group_id}", headers=headers)
    assert r.status_code == 404


def test_create_invitation_success(live_server_url="http://localhost:8000"):
    """Test crear invitación exitosamente."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {"name": "Grupo con Invitaciones", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Crear invitación
    invitation_data = {
        "email": "invitado@example.com",
        "message": "¡Únete a nuestro grupo de lectura!"
    }
    r = c.post(f"/groups/{group_id}/invitations", json=invitation_data, headers=headers)
    assert r.status_code == 201
    
    invitation = r.json()
    assert invitation["email"] == invitation_data["email"]
    assert invitation["message"] == invitation_data["message"]
    assert invitation["group_id"] == group_id


def test_get_group_members(live_server_url="http://localhost:8000"):
    """Test obtener miembros de un grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    username, token = _register_and_login(c)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear grupo
    group_data = {"name": "Grupo con Miembros", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Obtener miembros
    r = c.get(f"/groups/{group_id}/members", headers=headers)
    assert r.status_code == 200
    
    members = r.json()
    assert len(members) == 1  # Solo el creador
    assert members[0]["role"] == "admin"
    assert members[0]["user"]["username"] == username


def test_add_member_success(live_server_url="http://localhost:8000"):
    """Test añadir miembro a un grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Crear dos usuarios
    username1, token1 = _register_and_login(c)
    username2, token2 = _register_and_login(c)
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Usuario 1 crea grupo
    group_data = {"name": "Grupo Compartido", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers1)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Obtener ID del usuario 2
    r = c.get("/auth/me", headers=headers2)
    assert r.status_code == 200
    user2_id = r.json()["id"]
    
    # Usuario 1 añade usuario 2 al grupo
    member_data = {"user_id": user2_id, "role": "member"}
    r = c.post(f"/groups/{group_id}/members", json=member_data, headers=headers1)
    assert r.status_code == 201
    
    member = r.json()
    assert member["user_id"] == user2_id
    assert member["role"] == "member"
    
    # Verificar que el usuario 2 puede ver el grupo
    r = c.get("/groups/", headers=headers2)
    assert r.status_code == 200
    groups = r.json()
    assert len(groups) == 1
    assert groups[0]["id"] == group_id


def test_unauthorized_group_access(live_server_url="http://localhost:8000"):
    """Test acceso no autorizado a grupo."""
    c = Client(base_url=live_server_url, timeout=10.0)
    
    # Usuario 1 crea grupo
    username1, token1 = _register_and_login(c)
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    group_data = {"name": "Grupo Privado", "description": "Descripción"}
    r = c.post("/groups/", json=group_data, headers=headers1)
    assert r.status_code == 201
    group_id = r.json()["id"]
    
    # Usuario 2 intenta acceder al grupo
    username2, token2 = _register_and_login(c)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    r = c.get(f"/groups/{group_id}", headers=headers2)
    assert r.status_code == 404  # No debería poder ver el grupo
