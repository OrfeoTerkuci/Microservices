import json

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel
from wrapper import find_user, get_all_users

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
) -> Response:
    """
    Get a user by its id.

    :param user_id: The id of the user.
    :return: The user with the given id.
    """
    # If no username or id is provided, return all users

    if not user_id and not username:
        try:
            users = get_all_users()
            return Response(
                status_code=status.HTTP_200_OK,
                content=json.dumps(
                    {
                        "users": [
                            {"id": user.id, "username": user.username} for user in users
                        ]
                    }
                ),
                media_type="application/json",
            )
        except Exception as e:
            return Response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=json.dumps({"error": str(e)}),
                media_type="application/json",
            )
    try:
        user = find_user(user_id=user_id, username=username)
        if user:
            return Response(
                status_code=status.HTTP_200_OK,
                content=json.dumps(
                    {"user": {"id": user.id, "username": user.username}}
                ),
                media_type="application/json",
            )
    except ValueError as e:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json.dumps({"error": "User not found"}),
        media_type="application/json",
    )
