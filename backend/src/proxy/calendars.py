import json

import httpx
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

router = APIRouter()


class CalendarShareModel(BaseModel):
    sharingUser: str = Field(
        ..., min_length=1, description="The user sharing the calendar"
    )
    receivingUser: str = Field(
        ..., min_length=1, description="The user receiving the calendar"
    )


def check_user_exists(username: str):
    try:
        response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
        return response.status_code == 200
    except httpx.ConnectError:
        return False

@router.get(
    "",
    summary="Get all shared calendars",
    description="Get all shared calendars.",
    responses={
        200: {
            "description": "All the shared calendars",
            "content": {
                "application/json": {
                    "example": {
                        "calendars": [
                            {"sharingUser": "john_doe", "receivingUser": "jane_doe"}
                        ]
                    }
                }
            },
        },
    },
)
async def get_calendars():
    """
    Get all shared calendars.

    :returns: A list of all shared calendars.
    """
    try:
        response = httpx.get("http://calendars-service:8000/api/shares")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.get(
    "/by/{username}",
    summary="Get all calendars shared by a user",
    description="Get all calendars shared by a specific user.",
    responses={
        200: {
            "description": "All the calendars shared by a user",
            "content": {
                "application/json": {
                    "example": {
                        "calendars": [
                            {"sharingUser": "john_doe", "receivingUser": "jane_doe"}
                        ]
                    }
                }
            },
        },
    },
)
async def get_calendars_by(username: str):
    """
    Get all calendars shared by a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    try:
        response = httpx.get(f"http://calendars-service:8000/api/shares/by/{username}")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.get(
    "/with/{username}",
    summary="Get all calendars shared with a user",
    description="Get all calendars shared with a specific user.",
    responses={
        200: {
            "description": "All the calendars shared with a user",
            "content": {
                "application/json": {
                    "example": {
                        "calendars": [
                            {"sharingUser": "john_doe", "receivingUser": "jane_doe"}
                        ]
                    }
                }
            },
        },
    },
)
async def get_calendars_with(username: str):
    """
    Get all calendars shared with a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    try:
        response = httpx.get(
            f"http://calendars-service:8000/api/shares/with/{username}"
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.get(
    "/by/{username}/with/{receivingUser}",
    summary="Search for a specific sharing user and receiving user",
    description="Get a specific shared calendar by sharing user and receiving user.",
    responses={
        200: {
            "description": "Result for a specific sharing user and receiving user",
            "content": {
                "application/json": {
                    "example": {
                        "calendars": [
                            {"sharingUser": "john_doe", "receivingUser": "jane_doe"}
                        ]
                    }
                }
            },
        },
    },
)
async def get_calendars_by_with(username: str, receivingUser: str):
    """
    Get all calendars shared by a user with another user.

    :param username: The user to get shared calendars for.
    :param receivingUser: The user to get shared calendars with.

    :returns: A list of shared calendars.
    """
    try:
        response = httpx.get(
            f"http://calendars-service:8000/api/shares/by/{username}/with/{receivingUser}"
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.post(
    "",
    summary="Share a calendar",
    description="Share a calendar from one user with another.",
    responses={
        200: {
            "description": "Calendar shared",
            "content": {
                "application/json": {
                    "example": {
                        "calendar": {
                            "sharingUser": "john_doe",
                            "receivingUser": "jane_doe",
                        }
                    }
                }
            },
        },
        404: {
            "description": "Sharing or receiving user not found",
            "content": {
                "application/json": {"example": {"error": "Sharing user not found"}}
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def share_calendar(calendar: CalendarShareModel):
    # Check that both users exist

    if not check_user_exists(calendar.sharingUser):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Sharing user not found"}),
            media_type="application/json",
        )
    if not check_user_exists(calendar.receivingUser):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Receiving user not found"}),
            media_type="application/json",
        )
    # Share calendar

    try:
        response = httpx.post(
            "http://calendars-service:8000/api/shares",
            json={
                "sharingUser": calendar.sharingUser,
                "receivingUser": calendar.receivingUser,
            },
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.delete(
    "",
    summary="Delete a calendar share",
    description="Delete a calendar share between two users.",
    responses={
        200: {
            "description": "Calendar share successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "calendar": {
                            "sharingUser": "john_doe",
                            "receivingUser": "jane_doe",
                        }
                    }
                }
            },
        },
        404: {
            "description": "Sharing or receiving user not found",
            "content": {
                "application/json": {"example": {"error": "Sharing user not found"}}
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def delete_calendar(calendar: CalendarShareModel):
    # Check that both users exist

    if not check_user_exists(calendar.sharingUser):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Sharing user not found"}),
            media_type="application/json",
        )
    if not check_user_exists(calendar.receivingUser):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Receiving user not found"}),
            media_type="application/json",
        )
    # Delete calendar

    try:
        response = httpx.delete(
            f"http://calendars-service:8000/api/shares/{calendar.sharingUser}/{calendar.receivingUser}"
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )
