from app.database import SessionLocal
from app.models.book import Book
from app.models.user import User

db = SessionLocal()

# Buscar usuarios por email
tulkas_palantus = db.query(User).filter(User.email == 'tulkaspalantus@protonmail.com').first()
tulkas_paladin = db.query(User).filter(User.email == 'tulkaspaladin@protonmail.com').first()

print("=== USUARIOS ===")
if tulkas_palantus:
    print(f"tulkaspalantus: {tulkas_palantus.id} - {tulkas_palantus.username}")
else:
    print("tulkaspalantus: NO ENCONTRADO")

if tulkas_paladin:
    print(f"tulkaspaladin: {tulkas_paladin.id} - {tulkas_paladin.username}")
else:
    print("tulkaspaladin: NO ENCONTRADO")

print()

if tulkas_palantus:
    # Todos los libros de tulkaspalantus
    all_books = db.query(Book).filter(Book.owner_id == tulkas_palantus.id).all()
    print(f"=== LIBROS DE TULKASPALANTUS (TOTAL: {len(all_books)}) ===")
    for book in all_books:
        archived = "ARCHIVADO" if book.is_archived else "ACTIVO"
        print(f"  - [{archived}] '{book.title}' (Status: {book.status})")
    
    # Solo libros activos (no archivados)
    active_books = db.query(Book).filter(
        Book.owner_id == tulkas_palantus.id,
        Book.is_archived == False
    ).all()
    print(f"\n=== LIBROS ACTIVOS DE TULKASPALANTUS: {len(active_books)} ===")
    for book in active_books:
        print(f"  - '{book.title}' (Status: {book.status})")

db.close()
