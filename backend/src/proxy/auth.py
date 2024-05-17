import httpx
from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter()


class UserModel(BaseModel):
    """
    Class for user model.
    """

    username: str
    password: str


@router.post(
    "/login",
    summary="Login user",
    description="Login with username and password",
    responses={
        200: {
            "description": "Login successful",
            "content": {"text/plain": {"example": "Login successful"}},
        },
        401: {
            "description": "Incorrect username or password",
            "content": {"text/plain": {"example": "Incorrect username or password"}},
        },
    },
)
async def login(user: UserModel) -> Response:
    """
    Authenticate user.

    :param user: UserModel object with username and password
    :return: Response with status code 200 if login is successful, 401 otherwise
    """
    response = httpx.post(
        "http://auth-service:8000/api/auth/login",
        json={"username": user.username, "password": user.password},
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.post(
    "/register",
    summary="Register user",
    description="Register user with username and password",
    responses={
        200: {
            "description": "User registered",
            "content": {"application/json": {"username": "john_doe"}},
        },
        400: {
            "description": "Missig username or password",
            "content": {
                "text/plain": {"example": "Username and password must be provided"}
            },
        },
        409: {
            "description": "User already exists",
            "content": {"text/plain": {"example": "Username already registered"}},
        },
    },
)
async def register(user: UserModel) -> Response:
    """
    Register user.

    :param user: UserModel object with username and password
    :return: Response with status code
    200 if registration is successful,
    400 if username or password is missing,
    409 if user already exists
    """
    response = httpx.post(
        "http://auth-service:8000/api/auth/register",
        json={"username": user.username, "password": user.password},
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )
