import json
from pydantic import BaseModel
from fastapi import APIRouter, Response, status
from wrapper import get_all_users
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
        content=json.dumps({"users": [user.username for user in get_all_users()]}),
    )