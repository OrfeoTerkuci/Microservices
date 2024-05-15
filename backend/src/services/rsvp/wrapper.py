import datetime
import enum
import os
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    create_engine,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    URL,
)

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import DeclarativeBase, relationship, Session, sessionmaker
from sqlalchemy.schema import PrimaryKeyConstraint


def get_env(var: str) -> str:
    """
    Return value of an environment variable, raise exception if not defined or empty.

    :param var: The name of the environment variable to retrieve.

    :returns: Value of the environment variable `var`.
    :raises RuntimeError: If the environment variable `var` is not defined or empty.
    """
    if value := os.getenv(var, ""):
        return value
    raise RuntimeError(f"{var} is not defined or empty")


def get_db_url() -> URL:
    """
    Build and return the database URL to connect with postgres.

    :returns: An SQLAlchemy URL object to connect with the appdb.
    :raises RuntimeError: In case of missing or incorrectly configured env vars.
    """
    # Read data from environment

    user = get_env("RSVP_DB_USER")
    password = get_env("RSVP_DB_PASSWORD")
    host = get_env("RSVP_DB_HOST")
    port_raw = get_env("RSVP_DB_PORT")
    db = get_env("RSVP_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid RSVP_DB_PORT: {port_raw}") from exc
    return URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=port,
        database=db,
    )


def get_session() -> Session:
    try:
        session_maker = sessionmaker(bind=create_engine(get_db_url()))
        session = session_maker()
    except RuntimeError as exc:
        # Temporary ugly fix to not crash testing

        session = Session()
    return session


class Base(DeclarativeBase):
    """
    Base class for model class
    """
