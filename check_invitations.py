from app.database import SessionLocal
from app.models.invitation import Invitation

db = SessionLocal()
invs = db.query(Invitation).all()
print(f'Total invitaciones: {len(invs)}')
for i in invs:
    print(f'ID: {i.id}')
    print(f'  Code: {i.code}')
    print(f'  Email: {i.email}')
    print(f'  Accepted: {i.is_accepted}')
    print(f'  Group ID: {i.group_id}')
    print('---')
db.close()
