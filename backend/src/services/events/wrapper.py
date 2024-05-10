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

    user = get_env("EVENTS_DB_USER")
    password = get_env("EVENTS_DB_PASSWORD")
    host = get_env("EVENTS_DB_HOST")
    port_raw = get_env("EVENTS_DB_PORT")
    db = get_env("EVENTS_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid EVENTS_DB_PORT: {port_raw}") from exc
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


class Event(Base):
    """
    Event model class
    """

    __tablename__ = "events"

    id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    organizerId = Column(SmallInteger, nullable=False)
    isPublic = Column(Boolean, nullable=False)


def create_event(
    title: str, description: str, date: datetime.date, organizerId: int, isPublic: bool
) -> Any:
    """
    Create an event with the given parameters.

    :param title: The title of the event.
    :param description: The description of the event.
    :param date: The date of the event.
    :param organizerId: The id of the organizer.
    :param isPublic: Whether the event is public or not.

    :returns: The created event.
    :raises IntegrityError: If the event could not be created.
    """
    event = Event(
        title=title,
        description=description,
        date=date,
        organizerId=organizerId,
        isPublic=isPublic,
    )
    session = get_session()
    session.add(event)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise exc
    return Event(
        id=event.id,
        title=event.title,
        description=event.description,
        date=str(event.date),
        organizerId=event.organizerId,
        isPublic=event.isPublic,
    )


def find_all_events() -> Any:
    """
    Get all events.

    :returns: A list of all events.
    """
    session = get_session()
    events = session.query(Event).all()
    return [
        Event(
            id=event.id,
            title=event.title,
            description=event.description,
            date=str(event.date),
            organizerId=event.organizerId,
            isPublic=event.isPublic,
        )
        for event in events
    ]


def find_event(event_id: int) -> Any:
    """
    Get an event by its id.

    :param event_id: The id of the event to retrieve.

    :returns: The event with the given id.
    """
    session = get_session()
    event = session.query(Event).filter(Event.id == event_id).first()
    return (
        Event(
            id=event.id,
            title=event.title,
            description=event.description,
            date=str(event.date),
            organizerId=event.organizerId,
            isPublic=event.isPublic,
        )
        if event
        else None
    )


def update_event(
    event_id: int,
    title: str,
    description: str,
    date: str,
    organizerId: int,
    isPublic: bool,
):
    """
    Update an event with the given parameters.

    :param event_id: The id of the event to update.
    :param title: The title of the event.
    :param description: The description of the event.
    :param date: The date of the event.
    :param organizerId: The id of the organizer.
    :param isPublic: Whether the event is public or not.

    :returns: The updated event.
    :raises IntegrityError: If the event could not be updated.
    """
    session = get_session()
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        return
    setattr(event, "title", title)
    setattr(event, "description", description)
    setattr(event, "date", date)
    setattr(event, "organizerId", organizerId)
    setattr(event, "isPublic", isPublic)
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        raise exc
    return


def delete_event(event_id: int):
    """
    Delete an event by its id.

    :param event_id: The id of the event to delete.
    """
    session = get_session()
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        return
    session.delete(event)
    try:
        session.commit()
        return
    except Exception as exc:
        session.rollback()
        raise exc
