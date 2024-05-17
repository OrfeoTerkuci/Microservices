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


@router.get(
    "",
    summary="Get user(s)",
    description="""Get user(s). If no query parameters are provided, 
    all users are returned. If only one query parameter is provided, 
    the search is filtered by that parameter (username or userId). 
    If both are provided, the search is done for a specific user.""",
    responses={
        200: {
            "description": "User / Users found",
            "content": {
                "application/json": {
                    "example": {"user": {"id": 1, "username": "john_doe"}}
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {"text/plain": {"example": "User not found"}},
        },
    },
)
async def get_user(
    user_id: int = Query(default=None),
    username: str = Query(default=None),
):
    """
    Get a user by its id.

    :param user_id: The id of the user.
    :param username: The username of the user.
    :return: The user with the given id, or all users that match the query parameters.
    The query parameters filter the users by id or username.
    If both are provided, the search is done for a specific user.
    If none are provided, all users are returned.
    """

    # If no username or id is provided, return all users

    if not user_id and not username:
        try:
            response = httpx.get("http://auth-service:8000/api/users")
            return Response(
                status_code=response.status_code,
                content=response.content,
                media_type="application/json",
            )
        except httpx.ConnectError:
            return Response(
                status_code=500,
                content={"error": "Internal server error"},
                media_type="application/json",
            )
    # Set the query parameters

    params = {}
    if user_id:
        params["user_id"] = user_id
    if username:
        params["username"] = username
    # Send the request to the auth service

    try:
        response = httpx.get(
            f"http://auth-service:8000/api/users",
            params=params,
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=500,
            content={"error": "Internal server error"},
            media_type="application/json",
        )
