import json

import httpx
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from wrapper import (
    delete_shared_calendar,
    get_all_shared_calendars,
    get_shared_by,
    get_shared_calendar,
    get_shared_with,
    share_calendar,
)

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
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "calendars": [
                    {
                        "sharingUser": shared_calendar.sharingUser,
                        "receivingUser": shared_calendar.receivingUser,
                    }
                    for shared_calendar in get_all_shared_calendars()
                ]
            }
        ),
        media_type="application/json",
    )


@router.get("/by/{username}")
def get_calendars_by(username: str):
    """
    Get all calendars shared by a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "calendars": [
                    {
                        "sharingUser": shared_calendar.sharingUser,
                        "receivingUser": shared_calendar.receivingUser,
                    }
                    for shared_calendar in get_shared_by(username)
                ]
            }
        ),
        media_type="application/json",
    )


@router.get("/with/{username}")
def get_calendars_with(username: str):
    """
    Get all calendars shared with a user.

    :param username: The user to get shared calendars for.

    :returns: A list of shared calendars.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "calendars": [
                    {
                        "sharingUser": shared_calendar.sharingUser,
                        "receivingUser": shared_calendar.receivingUser,
                    }
                    for shared_calendar in get_shared_with(username)
                ]
            }
        ),
        media_type="application/json",
    )


@router.get("/by/{sharingUser}/with/{receivingUser}")
def get_specific_shared_calendar(sharingUser: str, receivingUser: str):
    """
    Get a shared calendar.

    :param sharingUser: The user sharing the calendar.
    :param receivingUser: The user receiving the calendar.

    :returns: The shared calendar.
    """
    calendar = get_shared_calendar(sharingUser=sharingUser, receivingUser=receivingUser)
    if not calendar:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Calendar not found"}),
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "calendar": {
                    "sharingUser": calendar.sharingUser,
                    "receivingUser": calendar.receivingUser,
                }
            }
        ),
        media_type="application/json",
    )


@router.post("")
def share_calendar_route(calendar: CalendarShareModel):
    """
    Share a calendar.

    :param calendar: The calendar to share.

    :returns: The shared calendar.
    """
    try:
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
        share_calendar(
            sharingUser=calendar.sharingUser, receivingUser=calendar.receivingUser
        )
    except Exception as exc:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(exc)}),
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=json.dumps(
            {
                "calendar": {
                    "sharingUser": calendar.sharingUser,
                    "receivingUser": calendar.receivingUser,
                }
            }
        ),
        media_type="application/json",
    )


@router.delete("")
def delete_shared_calendar_route(calendar: CalendarShareModel):
    """
    Delete a shared calendar.

    :param calendar: The calendar to delete.
    """
    try:
        delete_shared_calendar(
            sharingUser=calendar.sharingUser, receivingUser=calendar.receivingUser
        )
    except Exception as exc:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(exc)}),
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "message": "Calendar share successfully deleted",
            }
        ),
        media_type="application/json",
    )
