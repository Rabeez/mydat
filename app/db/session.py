from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///app/db/data/main.db"

engine = sa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autoflush=True,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


# NOTE: Only needed to invoke DB session in FastAPI lifespan for shutdown event
get_db_context = contextmanager(get_db)


def create_db_and_tables() -> None:
    Base.metadata.create_all(bind=engine)
