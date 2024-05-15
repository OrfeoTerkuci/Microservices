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


class RSVP_STATUS(enum.Enum):
    """
    RSVP status enum
    """

    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"


class Base(DeclarativeBase):
    """
    Base class for model class
    """


class RsvpResponse(Base):
    """
    RSVP Responses model
    """

    __tablename__ = "rsvp_responses"

    eventId = Column(SmallInteger, primary_key=True)
    username = Column(String, primary_key=True)
    status = Column(String, default=RSVP_STATUS.MAYBE, nullable=False)
    # __table_args__ = PrimaryKeyConstraint("eventId", "username")


def create_response(eventId: int, username: str, status: RSVP_STATUS):
    response = RsvpResponse(eventId=eventId, username=username, status=status.value)

    session = get_session()
    session.add(response)
    try:
        session.commit()
    except (IntegrityError, OperationalError) as exc:
        session.rollback()
        raise exc
    return RsvpResponse(eventId=eventId, username=username, status=status)


def find_all_responses():
    session = get_session()
    responses = session.query(RsvpResponse).all()
    return [
        RsvpResponse(
            eventId=response.eventId, username=response.username, status=response.status
        )
        for response in responses
    ]


def find_response(eventId: int, username: str):
    if not (eventId or username):
        return None
    session = get_session()
    response = (
        session.query(RsvpResponse)
        .filter(RsvpResponse.eventId == eventId, RsvpResponse.username == username)
        .first()
    )
    return (
        RsvpResponse(
            eventId=response.eventId, username=response.username, status=response.status
        )
        if response
        else None
    )


def find_response_by_event(eventId: int):
    session = get_session()
    responses = (
        session.query(RsvpResponse).filter(RsvpResponse.eventId == eventId).all()
    )
    return [
        RsvpResponse(
            eventId=response.eventId, username=response.username, status=response.status
        )
        for response in responses
    ]


def find_responses_by_user(username: str):
    session = get_session()
    responses = (
        session.query(RsvpResponse).filter(RsvpResponse.username == username).all()
    )
    return [
        RsvpResponse(
            eventId=response.eventId, username=response.username, status=response.status
        )
        for response in responses
    ]


def update_response(eventId: int, username: str, status: RSVP_STATUS):
    session = get_session()
    response = session.query(RsvpResponse).get((eventId, username))
    if response:
        setattr(response, "status", status.value)
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
    return


def delete_response(eventId: int, username: str):
    session = get_session()
    response = session.query(RsvpResponse).get((eventId, username))
    if response:
        session.delete(response)
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
    return
