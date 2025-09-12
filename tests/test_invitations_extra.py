import uuid
from httpx import Client


def _register_and_login(client: Client):
    username = f"inv_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "SuperSegura123"
    r = client.post("/auth/register", json={"username": username, "password": password, "email": email})
    assert r.status_code == 201, r.text
    user = r.json()
    r = client.post("/auth/login", data={"username": username, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return user, token


def test_duplicate_pending_invitation_returns_400(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    admin, admin_token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crear grupo
    r = c.post("/groups/", json={"name": "G1", "description": "D"}, headers=headers)
    assert r.status_code == 201
    group_id = r.json()["id"]
    # Crear invitación
    email = f"{uuid.uuid4().hex[:6]}@example.com"
    invite = {"email": email, "message": "join"}
    r1 = c.post(f"/groups/{group_id}/invitations", json=invite, headers=headers)
    assert r1.status_code == 201, r1.text
    # Duplicada pendiente
    r2 = c.post(f"/groups/{group_id}/invitations", json=invite, headers=headers)
    assert r2.status_code == 400, r2.text


def test_respond_nonexistent_or_expired_invitation_returns_400_or_404(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    user, token = _register_and_login(c)
    headers = {"Authorization": f"Bearer {token}"}
    fake_invitation_id = str(uuid.uuid4())
    # Responder aceptación a invitación inexistente → 400 según implementación
    r = c.post(f"/groups/invitations/{fake_invitation_id}/respond", json={"accept": True}, headers=headers)
    assert r.status_code in {400, 404}, r.text


def test_list_invitations_requires_admin_behavior(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    admin, admin_token = _register_and_login(c)
    member, member_token = _register_and_login(c)
    admin_h = {"Authorization": f"Bearer {admin_token}"}
    member_h = {"Authorization": f"Bearer {member_token}"}
    # Crear grupo (admin será ADMIN)
    r = c.post("/groups/", json={"name": "G2", "description": "D"}, headers=admin_h)
    assert r.status_code == 201
    group_id = r.json()["id"]
    # No admin intentando listar: según el servicio actual devuelve [] (200). Comprobamos que no truena ni expone info.
    r = c.get(f"/groups/{group_id}/invitations", headers=member_h)
    assert r.status_code in {200, 404}
    if r.status_code == 200:
        assert r.json() == []
    # Admin lista OK
    r = c.get(f"/groups/{group_id}/invitations", headers=admin_h)
    assert r.status_code == 200


def test_invitation_by_code_and_accept(live_server_url="http://localhost:8000"):
    c = Client(base_url=live_server_url, timeout=10.0)
    admin, admin_token = _register_and_login(c)
    invitee, invitee_token = _register_and_login(c)
    admin_h = {"Authorization": f"Bearer {admin_token}"}
    invitee_h = {"Authorization": f"Bearer {invitee_token}"}
    # Crear grupo
    r = c.post("/groups/", json={"name": "G3", "description": "D"}, headers=admin_h)
    group_id = r.json()["id"]
    # Crear invitación
    email = invitee["email"]
    r = c.post(f"/groups/{group_id}/invitations", json={"email": email, "message": "join"}, headers=admin_h)
    assert r.status_code == 201
    inv = r.json()
    # Detectar nombre de campo para el código
    possible_code_fields = ['code', 'invitation_code', 'token', 'uuid', 'invite_code', 'key']
    invitation_code = None
    for f in possible_code_fields:
        if f in inv and inv[f]:
            invitation_code = inv[f]
            break
    if not invitation_code:
        # Fallback: intentar leer la invitación recién creada por listado admin
        r_list = c.get(f"/groups/{group_id}/invitations", headers=admin_h)
        assert r_list.status_code == 200
        for iv in r_list.json():
            for f in possible_code_fields:
                if f in iv and iv[f]:
                    invitation_code = iv[f]
                    break
            if invitation_code:
                break
    assert invitation_code, "No se encontró campo de código de invitación"
    # Obtener por code sin auth
    r = c.get(f"/groups/invitations/by-code/{invitation_code}")
    assert r.status_code == 200
    # Aceptar por code con el usuario invitado
    r = c.post(f"/groups/invitations/accept/{inv['code']}", headers=invitee_h)
    assert r.status_code == 200, r.text

