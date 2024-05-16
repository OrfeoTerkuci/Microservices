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
    response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
    return response.status_code == 200


@router.get("")
def get_calendars():
    """
    Get all shared calendars.

    :returns: A list of all shared calendars.
    """
    response = httpx.get("http://calendars-service:8000/api/shares")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.get("/by/{username}")
def get_calendars_by(username: str):
    """
    Get all calendars shared by a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    response = httpx.get(f"http://calendars-service:8000/api/shares/by/{username}")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.get("/with/{username}")
def get_calendars_with(username: str):
    """
    Get all calendars shared with a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    response = httpx.get(f"http://calendars-service:8000/api/shares/with/{username}")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.get("/by/{username}/with/{receivingUser}")
def get_calendars_by_with(username: str, receivingUser: str):
    """
    Get all calendars shared by a user with another user.

    :param username: The user to get shared calendars for.
    :param receivingUser: The user to get shared calendars with.

    :returns: A list of shared calendars.
    """
    response = httpx.get(
        f"http://calendars-service:8000/api/shares/by/{username}/with/{receivingUser}"
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.post("")
def share_calendar(calendar: CalendarShareModel):
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


@router.delete("")
def delete_calendar(calendar: CalendarShareModel):
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

    response = httpx.delete(
        f"http://calendars-service:8000/api/shares/{calendar.sharingUser}/{calendar.receivingUser}"
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )
