from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.interaction import Base

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# pool_pre_ping prevents stale database connections during local Docker restarts.
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_interaction_type_column()


def _ensure_interaction_type_column() -> None:
    inspector = inspect(engine)
    if "interactions" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("interactions")}
    if "interaction_type" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE interactions ADD COLUMN interaction_type VARCHAR(40) DEFAULT 'Meeting'"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()