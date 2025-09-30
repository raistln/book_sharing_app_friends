"""Tests for group service."""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.services.group_service import GroupService
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.models.invitation import Invitation
from app.schemas.group import GroupCreate, GroupUpdate, InvitationCreate, GroupMemberCreate

# Test data
TEST_USER_ID = uuid4()
TEST_GROUP_ID = uuid4()
TEST_INVITATION_ID = uuid4()
TEST_USER = User(id=TEST_USER_ID, username="testuser", email="test@example.com")
TEST_GROUP = Group(id=TEST_GROUP_ID, name="Test Group", description="Test Description", created_by=TEST_USER_ID)

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def group_service(mock_db):
    return GroupService(mock_db)

class TestGroupService:
    def test_create_group_success(self, group_service, mock_db):
        """Test creating a new group successfully."""
        group_data = GroupCreate(
            name="New Group",
            description="A new group"
        )
        
        # Mock the database add and commit
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        
        # Create a mock for the group that will be returned
        mock_group = MagicMock()
        mock_group.id = TEST_GROUP_ID
        mock_group.name = "New Group"
        mock_group.description = "A new group"
        mock_group.created_by = TEST_USER_ID
        
        # Set the side effect to set the id on the group object
        def set_id(group):
            if isinstance(group, Group):
                group.id = TEST_GROUP_ID
            return group
            
        mock_db.add.side_effect = set_id
        
        # Call the service
        result = group_service.create_group(group_data, TEST_USER_ID)
        
        # Verify the result
        assert result is not None
        assert hasattr(result, 'id')
        assert result.name == "New Group"
        assert result.created_by == TEST_USER_ID
        
        # Verify the group was added to the database
        assert mock_db.add.call_count == 2  # Group and GroupMember
        mock_db.commit.assert_called_once()
        
    def test_get_group_found(self, group_service, mock_db):
        """Test getting an existing group by ID."""
        # Mock the database query
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = TEST_GROUP
        
        # Call the service
        result = group_service.get_group(TEST_GROUP_ID, TEST_USER_ID)
        
        # Verify the result
        assert result is not None
        assert result.id == TEST_GROUP_ID
        assert result.name == "Test Group"
        
    def test_get_group_not_found(self, group_service, mock_db):
        """Test getting a non-existent group by ID."""
        # Mock the database query to return None
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None
        
        # Call the service
        result = group_service.get_group(TEST_GROUP_ID, TEST_USER_ID)
        
        # Verify the result is None when group not found
        assert result is None
        
    def test_update_group_success(self, group_service, mock_db):
        """Test updating an existing group."""
        # Create a mock group
        mock_group = MagicMock()
        mock_group.id = TEST_GROUP_ID
        mock_group.name = "Test Group"
        mock_group.description = "Test Description"
        
        # Mock get_group to return our mock group
        group_service.get_group = MagicMock(return_value=mock_group)
        
        # Mock is_group_admin to return True
        group_service.is_group_admin = MagicMock(return_value=True)
        
        update_data = GroupUpdate(
            name="Updated Group",
            description="Updated description"
        )
        
        # Call the service
        result = group_service.update_group(TEST_GROUP_ID, TEST_USER_ID, update_data)
        
        # Verify the result
        assert result is not None
        assert result.name == "Updated Group"
        assert result.description == "Updated description"
        
        # Verify the database was committed
        mock_db.commit.assert_called_once()
            
    def test_delete_group_success(self, group_service, mock_db):
        """Test deleting a group."""
        # Mock the database query to return our test group
        mock_db.query.return_value.filter.return_value.first.return_value = TEST_GROUP
        
        # Call the service
        result = group_service.delete_group(TEST_GROUP_ID, TEST_USER_ID)
        
        # Verify the result
        assert result is True
        
        # Verify the group was deleted and committed
        mock_db.delete.assert_called_once_with(TEST_GROUP)
        mock_db.commit.assert_called_once()
            
    def test_create_invitation_success(self, group_service, mock_db):
        """Test creating a group invitation."""
        # Mock dependencies
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing invitation
        
        # Create test data with required fields
        from app.schemas.invitation import InvitationCreate
        invitation_data = InvitationCreate(
            email="invitee@example.com",
            message="Te invito a unirte a mi grupo"
        )
        
        # Mock the group service method
        group_service.is_group_admin = MagicMock(return_value=True)
        group_service.get_group = MagicMock(return_value=MagicMock(id=TEST_GROUP_ID))
        
        # Mock the invitation that will be created
        mock_invitation = MagicMock()
        mock_invitation.id = TEST_INVITATION_ID
        mock_invitation.email = "invitee@example.com"
        mock_invitation.group_id = TEST_GROUP_ID
        mock_invitation.invited_by = TEST_USER_ID
        mock_invitation.message = "Te invito a unirte a mi grupo"
        
        # Mock the database add to return our mock invitation
        def mock_add(invitation):
            invitation.id = TEST_INVITATION_ID
            return invitation
            
        mock_db.add.side_effect = mock_add
        
        # Call the service
        result = group_service.create_invitation(
            group_id=TEST_GROUP_ID,
            user_id=TEST_USER_ID,
            invitation_data=invitation_data
        )
        
        # Verify the result
        assert result is not None
        assert result.email == "invitee@example.com"
        assert result.group_id == TEST_GROUP_ID
        assert result.invited_by == TEST_USER_ID
        assert result.message == "Te invito a unirte a mi grupo"
        
        # Verify the invitation was added to the database
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
    def test_respond_to_invitation_success(self, group_service, mock_db):
        """Test responding to a group invitation."""
        # Create a test invitation
        test_invitation = MagicMock()
        test_invitation.id = TEST_INVITATION_ID
        test_invitation.email = TEST_USER.email
        test_invitation.group_id = TEST_GROUP_ID
        test_invitation.invited_by = uuid4()
        test_invitation.is_accepted = None
        
        # Mock the database query to return our test invitation
        mock_db.query.return_value.filter.return_value.first.return_value = test_invitation
        
        # Create a mock user
        mock_user = MagicMock()
        mock_user.id = TEST_USER_ID
        mock_user.email = TEST_USER.email
        
        # Mock the user query to return our test user
        def mock_query_filter(*args, **kwargs):
            if 'email' in str(kwargs.get('_criterion')):
                return MagicMock(first=MagicMock(return_value=mock_user))
            return MagicMock(first=MagicMock(return_value=test_invitation))
            
        mock_db.query.return_value.filter.side_effect = mock_query_filter
        
        # Create a mock for the group member that will be returned
        mock_member = MagicMock()
        mock_member.user_id = TEST_USER_ID
        
        # Mock the add method to return our mock member
        def mock_add(member):
            member.id = uuid4()
            return member
            
        mock_db.add.side_effect = mock_add
        
        # Call the service to accept the invitation
        result = group_service.respond_to_invitation(
            invitation_id=TEST_INVITATION_ID,
            email=TEST_USER.email,
            accept=True
        )
        
        # Verify the result is the member that was added
        assert result is not None
        assert hasattr(result, 'user_id')
        
        # Verify the invitation status was updated
        assert test_invitation.is_accepted is True
        assert test_invitation.responded_at is not None
        
        # Verify the database was committed
        mock_db.commit.assert_called_once()
        
    def test_list_user_groups(self, group_service, mock_db):
        """Test listing groups for a user."""
        # Create test data
        test_groups = [
            Group(id=uuid4(), name="Group 1", created_by=TEST_USER_ID),
            Group(id=uuid4(), name="Group 2", created_by=uuid4())
        ]
        
        # Mock the database query
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = test_groups
        
        # Call the service
        result = group_service.get_user_groups(TEST_USER_ID)
        
        # Verify the result
        assert len(result) == 2
        assert result[0].name == "Group 1"
        assert result[1].name == "Group 2"
        
        # Verify the query was made correctly
        mock_db.query.assert_called_once()
        mock_db.query.return_value.join.assert_called_once()
        mock_db.query.return_value.join.return_value.filter.assert_called_once()
