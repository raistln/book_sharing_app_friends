from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

# Buscar usuario Samsagaz
user = db.query(User).filter(User.username == 'Samsagaz').first()

if user:
    print(f"Usuario encontrado:")
    print(f"  ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    print(f"  Verified: {user.is_verified}")
else:
    print("Usuario Samsagaz no encontrado")
    
    # Listar todos los usuarios
    all_users = db.query(User).all()
    print(f"\nUsuarios disponibles ({len(all_users)}):")
    for u in all_users[:10]:
        print(f"  - {u.username} ({u.email})")

db.close()
