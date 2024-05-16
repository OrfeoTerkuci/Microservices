import httpx
from fastapi import APIRouter, Query, Response
from pydantic import BaseModel

router = APIRouter()


class UserModel(BaseModel):
    """
    Class for user model.
    """

    username: str
    password: str


@router.get("")
def get_user(
    user_id: int = Query(default=None),
    username: str = Query(default=None),
):
    """
    Get a user by its id.

    :param user_id: The id of the user.
    :return: The user with the given id.
    """

    # If no username or id is provided, return all users

    if not user_id and not username:
        response = httpx.get("http://auth-service:8000/api/users")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    # Set the query parameters

    params = {}
    if user_id:
        params["user_id"] = user_id
    if username:
        params["username"] = username
    # Send the request to the auth service

    response = httpx.get(
        f"http://auth-service:8000/api/users",
        params=params,
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )
