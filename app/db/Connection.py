from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine, select

from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=settings.debug, connect_args=connect_args)


def create_db_and_tables() -> None:
    from app.db import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def seed_catalog_items() -> None:
    from app.db.models import CatalogItem

    seed_data = [
        {
            "name": "Classic Fire Truck",
            "category": "City",
            "description": "A compact city fire truck with ladder and water tools.",
        },
        {
            "name": "Galaxy Explorer",
            "category": "Space",
            "description": "A retro-style exploration ship for deep-space missions.",
        },
        {
            "name": "Harbor Cargo Crane",
            "category": "Technic",
            "description": "A heavy-duty crane used to load and unload dock containers.",
        },
        {
            "name": "Medieval Market Stall",
            "category": "Castle",
            "description": "A market stand with produce crates and village accessories.",
        },
        {
            "name": "Desert Rally Racer",
            "category": "Speed",
            "description": "An off-road race car tuned for sand dunes and jumps.",
        },
    ]

    with Session(engine) as session:
        existing = session.exec(select(CatalogItem.id).limit(1)).first()
        if existing is not None:
            return

        session.add_all([CatalogItem(**item) for item in seed_data])
        session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def check_database_connection() -> tuple[bool, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Database connection healthy"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)
