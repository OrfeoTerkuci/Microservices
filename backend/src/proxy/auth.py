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


@router.post("/login")
async def login(user: UserModel) -> Response:
    """
    Authenticate user.
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


@router.post("/register")
async def register(user: UserModel) -> Response:
    """
    Register user.
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
