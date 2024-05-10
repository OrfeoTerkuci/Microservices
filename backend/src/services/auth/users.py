import json

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from wrapper import find_user, get_all_users

router = APIRouter()


class UserModel(BaseModel):
    """
    Class for user model.
    """

    username: str
    password: str


@router.get("/")
async def get_users() -> Response:
    """
    Get all users.

    :return: List of users
    """
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "users": [
                    {"id": user.id, "username": user.username}
                    for user in get_all_users()
                ]
            }
        ),
    )


@router.get("/{user_id}")
async def get_user(user_id: int) -> Response:
    """
    Get a user by its id.

    :param user_id: The id of the user.
    :return: The user with the given id.
    """
    user = find_user(user_id=user_id)
    if not user:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "User not found"}),
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"user": user.username}),
    )
