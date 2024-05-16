"""
Handles the database connection and operations for the authentication service.
"""

import os
from typing import Any

from sqlalchemy import (
    Column,
    create_engine,
    SmallInteger,
    String,
    URL,
)

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


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

    user = get_env("AUTH_DB_USER")
    password = get_env("AUTH_DB_PASSWORD")
    host = get_env("AUTH_DB_HOST")
    port_raw = get_env("AUTH_DB_PORT")
    db = get_env("AUTH_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid AUTH_DB_PORT: {port_raw}") from exc

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


class User(Base):
    """
    Model representing a user.
    """

    __tablename__ = "users"

    id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)


def create_user(
    username: str,
    password: str,
) -> User:
    """
    Creates a user.

    :param username: Username of the user.
    :param password: Password of the user.

    :raises ValueError: If the user with the given username already exists.

    :return: The created User instance.
    """
    session = get_session()
    if session.query(User).filter(User.username == username).first():
        raise ValueError("User already exists")

    new_user = User(username=username, password=password)
    try:
        session.add(new_user)
        session.commit()
        return User(username=username, password=password, id=new_user.id)
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error creating user") from exc_inner


def find_user(username: str | None = None, user_id: int | None = None) -> User:
    """
    Finds a user based on its username and/or id.

    :param username: Username of the user to find.
    :param user_id: ID of the user to find.

    :raises ValueError: If the user with the given username
    and/or id is not found in the database.
    :return: The found User instance.
    """
    if not username and not user_id:
        raise ValueError("No username or id provided")
    session = get_session()
    try:
        user = (
            (session.query(User).filter(User.username == username).first())
            if username is not None
            else session.query(User).filter(User.id == user_id).first()
        )
    except OperationalError as se:
        raise ValueError("Error getting user:", se) from se

    if user is None:
        raise ValueError(
            f"User with username {username} and id {user_id} not found in the database"
        )

    return User(username=user.username, password=user.password, id=user.id)


def get_all_users() -> list[User]:
    """
    Gets all users from the database.

    :raises ValueError: If there is an error getting the users.

    :return: List of all User instances.
    """
    session = get_session()
    try:
        users = session.query(User).all()
        return [
            User(username=user.username, password=user.password, id=user.id)
            for user in users
        ]
    except OperationalError as se:
        raise ValueError("Error getting users:", se) from se


def update_user(user_id: int, **kwargs: Any) -> User:
    r"""
    Updates a user's attributes.

    :param user_id: ID of the user to update.
    :param kwargs: Updated attributes for the user.

    :raises ValueError: If the user with the given ID is not found in the database.

    :return: The updated User instance.
    """
    session = get_session()

    if not (user := session.query(User).filter(User.id == user_id).first()):
        raise ValueError(f"User with ID {user_id} not found in the database")

    for key, value in kwargs.items():
        if key in ["username", "password"]:
            setattr(user, key, value)
    try:
        session.commit()
        return User(username=user.username, password=user.password, id=user.id)
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error updating user") from exc_inner


def delete_user(user_id: int) -> None:
    """
    Deletes a user based on its ID.
    :param user_id: ID of the user to delete.
    :raises ValueError: If the user with the given ID is not found in the database
    """
    session = get_session()

    if not (user := session.query(User).filter(User.id == user_id).first()):
        raise ValueError(f"User with ID {user_id} not found in the database")
    try:
        session.delete(user)
        session.commit()
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error deleting user") from exc_inner
