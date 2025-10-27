"""Tests unitarios del NotificationService"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.notification import NotificationType, NotificationPriority
from app.services.notification_service import NotificationService


def _create_user(db: Session, username: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash="hash",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_and_get_notifications(db_session: Session) -> None:
    service = NotificationService(db_session)
    user = _create_user(db_session, "user_notif")

    notif = service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.NEW_MESSAGE,
        title="Nuevo mensaje",
        message="Tienes un mensaje nuevo",
        priority=NotificationPriority.MEDIUM,
        data={"foo": "bar"},
    )

    assert notif.id is not None

    results = service.get_user_notifications(user_id=user.id)
    assert len(results) == 1
    assert results[0].title == "Nuevo mensaje"


def test_filters_read_and_type(db_session: Session) -> None:
    service = NotificationService(db_session)
    user = _create_user(db_session, "user_filters")

    first = service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.NEW_MESSAGE,
        title="Mensaje",
        message="mensaje",
        priority=NotificationPriority.MEDIUM,
    )
    service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.LOAN_REQUEST,
        title="Préstamo",
        message="préstamo",
        priority=NotificationPriority.HIGH,
    )

    service.mark_as_read(first.id)

    unread = service.get_user_notifications(user_id=user.id, is_read=False)
    assert len(unread) == 1
    assert unread[0].type == NotificationType.LOAN_REQUEST

    loans = service.get_user_notifications(user_id=user.id, notification_type=NotificationType.LOAN_REQUEST)
    assert len(loans) == 1
    assert loans[0].title == "Préstamo"


def test_mark_and_delete(db_session: Session) -> None:
    service = NotificationService(db_session)
    user = _create_user(db_session, "user_mark")

    notif = service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.NEW_MESSAGE,
        title="Mensaje",
        message="mensaje",
        priority=NotificationPriority.LOW,
    )

    assert service.get_unread_count(user.id) == 1

    service.mark_all_as_read(user.id)
    assert service.get_unread_count(user.id) == 0

    deleted = service.delete_notification(notif.id)
    assert deleted is True
    assert service.get_notification(notif.id) is None


def test_stats_grouping(db_session: Session) -> None:
    service = NotificationService(db_session)
    user = _create_user(db_session, "user_stats")

    now = datetime.utcnow()
    for _ in range(2):
        service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.NEW_MESSAGE,
            title="Mensaje",
            message="mensaje",
            priority=NotificationPriority.MEDIUM,
        )
    service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.LOAN_REQUEST,
        title="Préstamo",
        message="préstamo",
        priority=NotificationPriority.HIGH,
    )

    stats = service.get_stats(user.id)
    assert stats["total"] == 3
    assert stats["unread"] == 3
    assert stats["by_type"]["NEW_MESSAGE"] == 2
    assert stats["by_type"]["LOAN_REQUEST"] == 1
    assert stats["by_priority"]["medium"] == 2
    assert stats["by_priority"]["high"] == 1


def test_get_user_notifications_with_pagination(db_session: Session) -> None:
    service = NotificationService(db_session)
    user = _create_user(db_session, "user_page")

    for i in range(5):
        service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.NEW_MESSAGE,
            title=f"Notif {i}",
            message="mensaje",
            priority=NotificationPriority.MEDIUM,
        )

    first_batch = service.get_user_notifications(user.id, limit=2, offset=0)
    assert len(first_batch) == 2
    second_batch = service.get_user_notifications(user.id, limit=2, offset=2)
    assert len(second_batch) == 2
    ids_first = {n.id for n in first_batch}
    ids_second = {n.id for n in second_batch}
    assert ids_first.isdisjoint(ids_second)
