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

    user = get_env("INVITES_DB_USER")
    password = get_env("INVITES_DB_PASSWORD")
    host = get_env("INVITES_DB_HOST")
    port_raw = get_env("INVITES_DB_PORT")
    db = get_env("INVITES_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid INVITES_DB_PORT: {port_raw}") from exc
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


class INVITE_STATUS(enum.Enum):
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"
    PENDING = "PENDING"


class Invite(Base):
    """
    Model class for invites table
    """

    __tablename__ = "invites"

    eventId = Column(SmallInteger, primary_key=True)
    username = Column(String, primary_key=True)
    status = Column(String, default=INVITE_STATUS.PENDING, nullable=False)
    # __table_args__ = PrimaryKeyConstraint("eventId", "username")


def create_invite(eventId: int, username: str, status: INVITE_STATUS):
    invite = Invite(eventId=eventId, username=username, status=status.value)

    session = get_session()
    session.add(invite)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise exc
    return Invite(eventId=eventId, username=username, status=status)


def find_all_invites():
    session = get_session()
    invites = session.query(Invite).all()
    return [
        Invite(eventId=invite.eventId, username=invite.username, status=invite.status)
        for invite in invites
    ]


def find_invite(eventId: int, username: str):
    if not (eventId or username):
        return None
    session = get_session()
    invite = (
        session.query(Invite)
        .filter(Invite.eventId == eventId, Invite.username == username)
        .first()
    )
    return (
        Invite(eventId=invite.eventId, username=invite.username, status=invite.status)
        if invite
        else None
    )


def find_invites_by_event(eventId: int):
    session = get_session()
    invites = session.query(Invite).filter(Invite.eventId == eventId).all()
    return [
        Invite(eventId=invite.eventId, username=invite.username, status=invite.status)
        for invite in invites
    ]


def find_invites_by_user(username: str):
    session = get_session()
    invites = session.query(Invite).filter(Invite.username == username).all()
    return [
        Invite(eventId=invite.eventId, username=invite.username, status=invite.status)
        for invite in invites
    ]


def update_invite(eventId: int, username: str, status: INVITE_STATUS):
    session = get_session()
    invite = session.query(Invite).get((eventId, username))
    if invite:
        setattr(invite, "status", status)
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
    return


def delete_invite(eventId: int, username: str):
    session = get_session()
    invite = session.query(Invite).get((eventId, username))
    if invite:
        session.delete(invite)
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
    return
