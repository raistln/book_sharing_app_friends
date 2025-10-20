from app.database import SessionLocal
from app.models.group import GroupMember
from app.models.book import Book
from uuid import UUID

db = SessionLocal()

# Usuario actual
user_id = UUID('4b7e3bbb-e531-4086-bcac-9c5129e8c52c')
group_id = UUID('ae02f3d6-5675-4cf1-b48f-c8c17037d3c6')

print(f"Usuario: {user_id}")
print(f"Grupo: {group_id}")
print()

# Obtener grupos del usuario
user_groups = db.query(GroupMember).filter(
    GroupMember.user_id == user_id,
    GroupMember.group_id == group_id
).all()

print(f"Membresías del usuario en el grupo: {len(user_groups)}")
for gm in user_groups:
    print(f"  - Grupo: {gm.group_id}, Rol: {gm.role}")
print()

# Obtener todos los miembros del grupo (excluyendo usuario actual)
group_members = db.query(GroupMember).filter(
    GroupMember.group_id == group_id,
    GroupMember.user_id != user_id
).all()

print(f"Otros miembros del grupo: {len(group_members)}")
member_ids = set()
for gm in group_members:
    member_ids.add(gm.user_id)
    print(f"  - Usuario: {gm.user_id}")
print()

# Buscar libros de esos miembros
if member_ids:
    books = db.query(Book).filter(
        Book.owner_id.in_(member_ids)
    ).all()
    
    print(f"Libros encontrados: {len(books)}")
    for book in books:
        print(f"  - '{book.title}' de {book.author} (Owner: {book.owner_id}, Status: {book.status})")
else:
    print("No hay otros miembros en el grupo")

# Verificar si hay libros en general
all_books = db.query(Book).all()
print(f"\nTotal de libros en la BD: {len(all_books)}")

# Verificar libros del usuario actual
user_books = db.query(Book).filter(
    Book.owner_id == user_id
).all()
print(f"Libros del usuario actual: {len(user_books)}")

# Verificar libros del otro miembro
if member_ids:
    other_member_id = list(member_ids)[0]
    other_books = db.query(Book).filter(
        Book.owner_id == other_member_id
    ).all()
    print(f"Libros del otro miembro ({other_member_id}): {len(other_books)}")
    for book in other_books:
        print(f"  - '{book.title}' de {book.author}")

db.close()
