import json

from dependencies import authenticate_user, get_password_hash
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from wrapper import create_user


router = APIRouter()


class UserModel(BaseModel):
    """
    Class for user model.
    """

    username: str
    password: str


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
    # authenticate user
    # Potentially use decrypt the form data first to be able to use the
    #  username and password for later
    # raise exception if user is not found

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
