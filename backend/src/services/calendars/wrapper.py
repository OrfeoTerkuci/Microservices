import datetime
import os
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    create_engine,
    Date,
    ForeignKey,
    SmallInteger,
    String,
    URL,
)

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import DeclarativeBase, relationship, Session, sessionmaker


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

    user = get_env("CALENDARS_DB_USER")
    password = get_env("CALENDARS_DB_PASSWORD")
    host = get_env("CALENDARS_DB_HOST")
    port_raw = get_env("CALENDARS_DB_PORT")
    db = get_env("CALENDARS_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid CALENDARS_DB_PORT: {port_raw}") from exc
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


class SharedCalendar(Base):
    """
    Model class for shared calendars
    """

    __tablename__ = "shared_calendars"

    sharingUser = Column(String, primary_key=True)
    receivingUser = Column(String, primary_key=True)


def share_calendar(sharingUser: str, receivingUser: str) -> Any:
    """
    Share a calendar with another user.

    :param sharingUser: The user sharing the calendar.
    :param receivingUser: The user receiving the calendar.

    :returns: The shared calendar.
    """
    session = get_session()
    shared_calendar = SharedCalendar(
        sharingUser=sharingUser, receivingUser=receivingUser
    )
    session.add(shared_calendar)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise exc
    return SharedCalendar(sharingUser=sharingUser, receivingUser=receivingUser)


def get_all_shared_calendars() -> Any:
    """
    Get all shared calendars.

    :returns: A list of all shared calendars.
    """
    session = get_session()
    return [
        SharedCalendar(
            sharingUser=shared_calendar.sharingUser,
            receivingUser=shared_calendar.receivingUser,
        )
        for shared_calendar in session.query(SharedCalendar).all()
    ]


def get_shared_by(username: str):
    """
    Get all calendars shared by a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    session = get_session()
    return [
        SharedCalendar(
            sharingUser=shared_calendar.sharingUser,
            receivingUser=shared_calendar.receivingUser,
        )
        for shared_calendar in session.query(SharedCalendar)
        .filter_by(sharingUser=username)
        .all()
    ]


def get_shared_with(username: str):
    """
    Get all calendars shared with a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    session = get_session()
    return [
        SharedCalendar(
            sharingUser=shared_calendar.sharingUser,
            receivingUser=shared_calendar.receivingUser,
        )
        for shared_calendar in session.query(SharedCalendar)
        .filter_by(receivingUser=username)
        .all()
    ]


def get_shared_calendar(sharingUser: str, receivingUser: str):
    """
    Get a shared calendar.

    :param sharingUser: The user sharing the calendar.
    :param receivingUser: The user receiving the calendar.

    :returns: The shared calendar.
    """
    session = get_session()
    shared_calendar = (
        session.query(SharedCalendar)
        .filter_by(sharingUser=sharingUser, receivingUser=receivingUser)
        .first()
    )
    return (
        SharedCalendar(
            sharingUser=shared_calendar.sharingUser,
            receivingUser=shared_calendar.receivingUser,
        )
        if shared_calendar
        else None
    )


def delete_shared_calendar(sharingUser: str, receivingUser: str):
    """
    Delete a shared calendar.

    :param sharingUser: The user sharing the calendar.
    :param receivingUser: The user receiving the calendar.
    """
    session = get_session()
    calendar = (
        session.query(SharedCalendar)
        .filter_by(sharingUser=sharingUser, receivingUser=receivingUser)
        .first()
    )
    if not calendar:
        return
    try:
        session.delete(calendar)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise exc
