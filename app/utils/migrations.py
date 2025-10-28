"""Utility helpers for running Alembic migrations programmatically."""
from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import settings

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Apply all pending Alembic migrations using the active DATABASE_URL."""
    project_root = Path(__file__).resolve().parents[2]
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    logger.info("Executing Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    logger.info("Alembic migrations completed successfully")
