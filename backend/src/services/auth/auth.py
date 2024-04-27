import json

from dependencies import (
    authenticate_user,
    check_token_validity,
    create_user_token,
    get_password_hash,
)
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from wrapper import add_token, blacklist_token, create_user, find_user


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
    # create access token

    access_token = create_user_token(form_data.username, form_data.password)

    try:
        user = find_user(form_data.username)
        # add user token to database

        add_token(access_token, int(user.id))  # type: ignore
    except ValueError:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found",
        )
    # return access token

    return Response(
        status_code=status.HTTP_200_OK,
        content="Login successful",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@router.post("/register")
async def register(user: UserModel) -> Response:
    """
    Register endpoint for users to create an account.

    :param user: UserModel object with username and password
    :raises HTTPException: Username already registered
    :return: Username and cookie
    """

    # create user

    try:
        hashed_password = get_password_hash(user.password)
        user_instance = create_user(user.username, hashed_password)
    except ValueError:
        return Response(
            status_code=status.HTTP_409_CONFLICT, content="Username already registered"
        )
    # create access token

    access_token = create_user_token(user.username, user.password)

    # add user token to database

    try:
        add_token(access_token, int(user_instance.id))  # type: ignore
    except ValueError:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found",
        )
    # return username and access token

    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"username": user.username}),
        headers={"Authorization": f"Bearer {access_token}"},
    )


@router.post("/logout")
async def logout(request: Request) -> Response:
    """
    Logout endpoint for users to end their session.

    :param request: Request object

    :return: Success message
    """
    # get the token from the Authorization header

    cookie = request.headers.get("Authorization", None)
    if not (cookie or isinstance(cookie, str)):
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Not Authorized",
        )
    if not cookie.startswith("Bearer "):
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Not Authorized",
        )
    token = cookie.split(" ")[1]
    try:
        blacklist_token(token)
    except ValueError:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Token not found",
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"message": "User logged out"}),
    )


@router.get("/status")
async def get_status(request: Request) -> Response:
    """
    Status endpoint for users to check their session status.

    :param request: Request object

    :return: Success message
    """
    # get cookie from request headers

    cookie = request.headers.get("Authorization", None)
    if not (cookie or isinstance(cookie, str)):
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="No cookie provided in headers",
        )
    if not cookie.startswith("Bearer "):
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid cookie format",
        )
    token = cookie.split(" ")[1]

    # unpack cookie

    try:
        await check_token_validity(token)
    except HTTPException as exc:
        return Response(
            status_code=exc.status_code,
            content=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content="User session is active",
    )
