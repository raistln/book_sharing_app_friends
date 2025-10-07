"""
Pruebas unitarias para modelo User
"""
import uuid
from app.database import SessionLocal
from app.models.user import User

def test_user_is_active_edge_cases():
    """Test is_active field edge cases"""
    db = SessionLocal()
    try:
        # Create active user
        user1 = User(username=f"active_user_{uuid.uuid4().hex[:8]}", email=f"active{uuid.uuid4().hex[:8]}@example.com", password_hash="hash", is_active=True)
        db.add(user1)
        db.commit()
        db.refresh(user1)
        assert user1.is_active == True

        # Create inactive user
        user2 = User(username=f"inactive_user_{uuid.uuid4().hex[:8]}", email=f"inactive{uuid.uuid4().hex[:8]}@example.com", password_hash="hash", is_active=False)
        db.add(user2)
        db.commit()
        db.refresh(user2)
        assert user2.is_active == False

        # Deactivate active user
        user1.is_active = False
        db.commit()
    finally:
        db.close()


def test_user_unique_constraints():
    """Test unique constraints on username and email"""
    from sqlalchemy.exc import IntegrityError

    db = SessionLocal()
    try:
        # Create first user
        user1 = User(username=f"unique_user_{uuid.uuid4().hex[:8]}", email=f"unique{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
        db.add(user1)
        db.commit()

        # Try duplicate username
        user2 = User(username=user1.username, email=f"different{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
        db.add(user2)
        db.commit()  # Should fail
        assert False, "Should have raised IntegrityError for username"
    except IntegrityError:
        assert True
    finally:
        db.close()


def test_user_relationships():
    """Test user relationships"""
    from app.models.group import Group, GroupMember, GroupRole

    db = SessionLocal()
    try:
        user1 = User(username=f"user1_{uuid.uuid4().hex[:8]}", email=f"user1{uuid.uuid4().hex[:8]}@example.com", password_hash="hash", is_active=True)
        user2 = User(username=f"user2_{uuid.uuid4().hex[:8]}", email=f"user2{uuid.uuid4().hex[:8]}@example.com", password_hash="hash", is_active=True)
        db.add(user1)
        db.commit()
        db.refresh(user1)
        db.add(user2)
        db.commit()
        db.refresh(user2)

        group = Group(name="Test Group", description="Test", created_by=user1.id)
        db.add(group)
        db.commit()

        # Test created_groups
        assert len(user1.created_groups) == 1
        assert user1.created_groups[0].name == "Test Group"
        # Test group_memberships
        member = GroupMember(group_id=group.id, user_id=user2.id, role=GroupRole.MEMBER, invited_by=user1.id)
        db.add(member)
        db.commit()
        assert len(user2.group_memberships) == 1
    finally:
        db.close()
