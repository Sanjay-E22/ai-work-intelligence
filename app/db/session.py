
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    WHY: Provide a database session for each request.
    ARGS: None.
    RETURN: An active SQLAlchemy session.
    RAISE: Database connection errors when connecting.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
