import json
from typing import Optional

import bcrypt

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from wrapper import create_user, get_all_users, User

router = APIRouter()


class UserModel(BaseModel):
    """
    Class for user model.
    """

    username: str
    password: str


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


def authenticate_user(username: str, password: str) -> Optional[User]:
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


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Response:
    """
    Login for access token.

    :param form_data: Form data
    :return: Token
    :raises HTTPException: Incorrect username or password
    """

    if not (user := authenticate_user(form_data.username, form_data.password)):
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Incorrect username or password",
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content="Login successful",
    )


@router.post("/register")
async def register(user: UserModel) -> Response:
    """
    Register endpoint for users to create an account.

    :param user: UserModel object with username and password
    :raises HTTPException: Username already registered
    :return: Username and cookie
    """
    try:
        create_user(user.username, get_password_hash(user.password))
    except ValueError:
        return Response(
            status_code=status.HTTP_409_CONFLICT, content="Username already registered"
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=json.dumps({"username": user.username}),
    )
