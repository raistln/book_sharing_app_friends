from app.database import SessionLocal
from app.models.invitation import Invitation

db = SessionLocal()

# Buscar la última invitación
inv = db.query(Invitation).filter(
    Invitation.email == 'tulkaspaladin@protonmail.com'
).first()

if inv:
    print(f'Invitación encontrada:')
    print(f'  ID: {inv.id}')
    print(f'  Code: "{inv.code}"')
    print(f'  Code length: {len(inv.code)}')
    print(f'  Email: {inv.email}')
    print(f'  Accepted: {inv.is_accepted}')
    print(f'  Group ID: {inv.group_id}')
    
    # Intentar buscar por código
    print(f'\nBuscando por código...')
    inv_by_code = db.query(Invitation).filter(
        Invitation.code == inv.code,
        Invitation.is_accepted.is_(None)
    ).first()
    
    if inv_by_code:
        print('✓ Invitación encontrada por código!')
    else:
        print('✗ NO se encontró la invitación por código')
        
        # Buscar sin filtro de is_accepted
        inv_by_code2 = db.query(Invitation).filter(
            Invitation.code == inv.code
        ).first()
        
        if inv_by_code2:
            print(f'  Pero SÍ existe con is_accepted={inv_by_code2.is_accepted}')
else:
    print('No se encontró invitación para ese email')

db.close()
