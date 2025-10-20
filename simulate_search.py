from app.database import SessionLocal
from app.models.user import User
from app.models.group import GroupMember
from app.models.book import Book
from uuid import UUID

db = SessionLocal()

# Usuario actual: Samsagaz
current_user_id = UUID('4b7e3bbb-e531-4086-bcac-9c5129e8c52c')

print("=== SIMULANDO ENDPOINT /search/books ===")
print(f"Usuario actual: {current_user_id} (Samsagaz)")
print()

# 1. Obtener grupos del usuario
user_groups = db.query(GroupMember).filter(
    GroupMember.user_id == current_user_id
).all()

print(f"Grupos del usuario: {len(user_groups)}")
for gm in user_groups:
    print(f"  - Grupo: {gm.group_id}")

# 2. Obtener IDs de grupos
group_ids = [gm.group_id for gm in user_groups]
member_ids = set()

# 3. Obtener miembros de esos grupos (excluyendo usuario actual)
if group_ids:
    group_members = db.query(GroupMember).filter(
        GroupMember.group_id.in_(group_ids),
        GroupMember.user_id != current_user_id
    ).all()
    
    print(f"\nOtros miembros en los grupos: {len(group_members)}")
    for gm in group_members:
        member_ids.add(gm.user_id)
        print(f"  - Usuario: {gm.user_id}")

# 4. Buscar libros de esos miembros (no archivados)
print(f"\nBuscando libros de {len(member_ids)} miembros...")

if member_ids:
    # SIN filtro de archivado
    all_books = db.query(Book).filter(
        Book.owner_id.in_(member_ids)
    ).all()
    print(f"  Libros totales (sin filtro): {len(all_books)}")
    
    # CON filtro de archivado
    active_books = db.query(Book).filter(
        Book.owner_id.in_(member_ids),
        Book.is_archived == False
    ).all()
    print(f"  Libros activos (con filtro): {len(active_books)}")
    
    if active_books:
        print("\n=== LIBROS QUE DEBERÍAN APARECER ===")
        for book in active_books:
            print(f"  - '{book.title}' de {book.author}")
            print(f"    Owner: {book.owner_id}, Archived: {book.is_archived}, Status: {book.status}")
    else:
        print("\n❌ NO HAY LIBROS ACTIVOS")
        
        # Verificar por qué
        if all_books:
            print("\nPero SÍ hay libros sin filtro de archivado:")
            for book in all_books:
                print(f"  - '{book.title}' - Archived: {book.is_archived}")
else:
    print("❌ No hay otros miembros en los grupos")

db.close()
