"""
    This module contains functions
    that interact with the database for user authentication.
"""

import os
from typing import Any, Union

from sqlalchemy import (
    Boolean,
    Column,
    create_engine,
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

    user = get_env("AUTH_DB_USER")
    password = get_env("AUTH_DB_PASSWORD")
    host = get_env("AUTH_DB_HOST")
    port_raw = get_env("AUTH_DB_PORT")
    db = get_env("AUTH_DB_NAME")

    # Convert port to number

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid APP_DB_PORT: {port_raw}") from exc

    return URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=port,
        database=db,
    )


try:
    session_maker = sessionmaker(bind=create_engine(get_db_url()))
    session = session_maker()
except RuntimeError as exc:
    # Temporary ugly fix to not crash testing
    session = Session()


def get_session() -> Session:
    return session


session = get_session()


class Base(DeclarativeBase):
    """
    Base class for model class
    """


class UserModel(Base):
    """
    Model representing a user.
    """

    __tablename__ = "users"

    id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    tokens = relationship("TokenModel", back_populates="users", cascade="all, delete")


class TokenModel(Base):
    """
    Model representing a token.
    """

    __tablename__ = "tokens"

    id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(SmallInteger, ForeignKey("users.id"), nullable=False)
    valid = Column(Boolean, nullable=False, default=True)

    users = relationship("UserModel", back_populates="tokens")


def create_user(
    username: str,
    password: str,
) -> UserModel:
    """
    Creates a user.

    :param username: Username of the user.
    :param password: Password of the user.

    :raises ValueError: If the user with the given username already exists.

    :return: The created UserModel instance.
    """
    if session.query(UserModel).filter(UserModel.username == username).first():
        raise ValueError("User already exists")

    new_user = UserModel(username=username, password=password)
    try:
        session.add(new_user)
        session.commit()
        return new_user
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error creating user") from exc_inner


def find_user(
    username: Union[str, None] = None, user_id: Union[int, None] = None
) -> UserModel:
    """
    Finds a user based on its username and/or id.

    :param username: Username of the user to find.
    :param user_id: ID of the user to find.

    :raises ValueError: If the user with the given username
    and/or id is not found in the database.
    :return: The found UserModel instance.
    """
    if not username and not user_id:
        raise ValueError("No username or id provided")

    try:
        user = (
            (session.query(UserModel).filter(UserModel.username == username).first())
            if username is not None
            else session.query(UserModel).filter(UserModel.id == user_id).first()
        )
    except OperationalError as se:
        raise ValueError("Error getting user:", se) from se

    if user is None:
        raise ValueError(
            f"User with username {username} and id {user_id} not found in the database"
        )

    return user


def get_all_users() -> list[UserModel]:
    """
    Gets all users from the database.

    :raises ValueError: If there is an error getting the users.

    :return: List of all UserModel instances.
    """
    try:
        return session.query(UserModel).all()
    except OperationalError as se:
        raise ValueError("Error getting users:", se) from se


def update_user(user_id: int, **kwargs: Any) -> UserModel:
    r"""
    Updates a user's attributes.

    :param user_id: ID of the user to update.
    :param kwargs: Updated attributes for the user.

    :raises ValueError: If the user with the given ID is not found in the database.

    :return: The updated UserModel instance.
    """

    if not (user := session.query(UserModel).filter(UserModel.id == user_id).first()):
        raise ValueError(f"User with ID {user_id} not found in the database")

    for key, value in kwargs.items():
        if key in ["username", "password"]:
            setattr(user, key, value)
    try:
        session.commit()
        return user
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error updating user") from exc_inner


def delete_user(user_id: int) -> None:
    """
    Deletes a user based on its ID.
    :param user_id: ID of the user to delete.
    :raises ValueError: If the user with the given ID is not found in the database
    """

    if not (user := session.query(UserModel).filter(UserModel.id == user_id).first()):
        raise ValueError(f"User with ID {user_id} not found in the database")
    try:
        session.delete(user)
        session.commit()
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError("Error deleting user") from exc_inner


def add_token(token: str, user_id: int) -> None:
    """
    Adds a token to the database.

    :param token: Token.
    :param user_id: ID of the user.

    :raises ValueError: If the token already exists in the database.
    """
    if session.query(TokenModel).filter(TokenModel.token == token).first():
        raise ValueError(f"Token {token} already exists in the database")
    try:
        new_token = TokenModel(token=token, user_id=user_id)
        session.add(new_token)
        session.commit()
    except IntegrityError as exc_inner:
        session.rollback()
        raise ValueError(f"Token {token} already exists in the database") from exc_inner


def blacklist_token(token_value: str) -> None:
    """
    Blacklists a token in the database.

    :param token_value: Token.

    :raises ValueError: If the token does not exist in the database.
    """
    # check if token exists
    try:
        if not (
            token := session.query(TokenModel)
            .filter(TokenModel.token == token_value)
            .first()
        ):
            raise ValueError(f"Token {token_value} not found in the database")

        setattr(token, "valid", True)
        session.commit()
    except ValueError as se:
        session.rollback()
        raise ValueError(f"Token {token_value} not found in the database") from se
    except OperationalError as se:
        session.rollback()
        raise ValueError("Error blacklisting token:", se) from se


def get_user_tokens(u_id: int) -> list[TokenModel]:
    """
    Gets all tokens from the database for a specific user.

    :param u_id: User ID.

    :raises ValueError: If there is an error getting the tokens.

    :return: List of all TokenModel instances.
    """
    try:
        return session.query(TokenModel).filter(TokenModel.user_id == u_id).all()
    except OperationalError as se:
        raise ValueError("Error getting tokens:", se) from se


def get_all_tokens() -> list[TokenModel]:
    """
    Gets all tokens from the database.

    :raises ValueError: If there is an error getting the tokens.

    :return: List of all TokenModel instances.
    """
    try:
        return session.query(TokenModel).all()
    except OperationalError as se:
        raise ValueError("Error getting tokens:", se) from se


def get_token(token: str) -> TokenModel | None:
    """
    Gets a token from the database.

    :param token: Token.

    :raises ValueError: If there is an error while getting the token.

    :return: TokenModel instance.
    """
    try:
        return session.query(TokenModel).filter(TokenModel.token == token).first()
    except OperationalError as se:
        raise ValueError("Error getting token:", se) from se
