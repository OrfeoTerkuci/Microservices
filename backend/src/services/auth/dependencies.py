"""
Dependencies for the API.

This module contains all the dependencies for the API, such as the security and roles.
"""

# Imports
import datetime
from typing import Annotated, Any, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from wrapper import find_user, get_all_users, get_token, UserModel

# Constants
# openssl rand -hex 32
SECRET_KEY = "f3c141d132a72394ff1a30d814c71216b6b8a5cc581fb233297e4ef3a8dcf7ad"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOWEST_ROLE = "default"


class Token(BaseModel):
    """
    Class for token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Class for token data.
    """

    username: str


# oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict[str, Any], expires_delta: datetime.timedelta) -> Any:
    """
    Create access token.

    :param data: Data
    :param expires_delta: Expiration delta (optional).
     Default is 15 minutes.
    :return: Encoded JWT
    """
    to_encode = data.copy()
    expire = datetime.datetime.now() + (
        expires_delta if expires_delta else datetime.timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# helper functions
def create_user_token(username: str, password: str) -> str:
    """
    Create a user access token.

    :param username: Username
    :param password: Password
    :return: access token
    """
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": username, "password": password},
        expires_delta=access_token_expires,
    )
    return str(access_token)


def verify_password(plain_password: str, crypt_password: str) -> bool:
    """
    Verify the password.

    :param plain_password: Plain password
    :param crypt_password: Hashed password
    :return: True if password is verified, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode(), crypt_password.encode())


def get_password_hash(password: str) -> str:
    """
    Get password hash.

    :param password: Password
    :return: Hashed password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    """
    Authenticate user.

    :param username: Username
    :param password: Password
    :return: UserModel if user is found, None otherwise
    """
    users = get_all_users()

    for user in users:
        if user.username == username and verify_password(password, str(user.password)):  # type: ignore
            return user
    return None


async def check_token_validity(token: str) -> None:
    """
    Checks if the token has expired or user is not found.

    :param token: Token
    :raises HTTPException:
                    If the token is invalid,
                    the username is not found in the token,
                    or the user does not have enough permissions.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        password: str = payload.get("password")
        # check if username is found
        if username is None or find_user(username=username) is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # check if token does not exist
        if not (token_instance := get_token(token)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found",
            )
        # check if token is invalid
        if not token_instance.valid:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> Any:
    """
    Get the current user based on token.

    :param token: Token, where the token depends on oauth2_scheme
    :return: PyUser
    :raises HTTPException: If the token is invalid,
                    the username is not found in the token,
                    or the user does not have enough permissions.
    """
    authenticate_value = "Bearer"
    # credentials_exception, in case of invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": authenticate_value},
    )

    # decode token and get username and role
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if (username := payload.get("username")) is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError as exc:
        raise expired_exception from exc
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    # get user from token_data
    if (user := find_user(username=username)) is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Security(get_current_user)]
) -> Any:
    """
    Get current active user.

    :param current_user: Current user
    :return: UserModel of the current user
    """
    return current_user
