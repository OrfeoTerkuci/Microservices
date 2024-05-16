import datetime
import json
import logging

import httpx
from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field

from wrapper import (
    create_invite,
    delete_invite,
    find_all_invites,
    find_invite,
    find_invites_by_event,
    find_invites_by_user,
    INVITE_STATUS,
    update_invite,
)

router = APIRouter()


class InviteModel(BaseModel):
    eventId: int
    username: str
    status: INVITE_STATUS


def check_user_exists(username: str):
    response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
    return response.status_code == 200


def check_event_exists(eventId: int):
    response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
    return response.status_code == 200


@router.get("")
def get_invite(
    username: str = Query(default=None, description="User's username"),
    eventId: int = Query(default=None, description="Event's ID"),
):
    """
    Get invite by user and event ID
    """
    if username and eventId:
        # Search for a specific invite
        invite = find_invite(eventId, username)
        if not invite:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Invite not found"}),
                media_type="application/json",
            )
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    f"invites": {
                        "eventId": invite.eventId,
                        "username": invite.username,
                        "status": invite.status,
                    }
                }
            ),
            media_type="application/json",
        )

    if username:
        invites = find_invites_by_user(username)
    elif eventId:
        invites = find_invites_by_event(eventId)
    else:
        invites = find_all_invites()
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "invites": [
                    {
                        "eventId": invite.eventId,
                        "username": invite.username,
                        "status": invite.status,
                    }
                    for invite in invites
                ]
            }
        ),
        media_type="application/json",
    )


@router.post("")
def add_invite(invite: InviteModel):
    """
    Create invite
    """
    try:
        # check if the user and event exist

        if not check_user_exists(invite.username):
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "User not found"}),
                media_type="application/json",
            )
        if not check_event_exists(invite.eventId):
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Event not found"}),
                media_type="application/json",
            )
        create_invite(invite.eventId, invite.username, invite.status)
        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps(
                {
                    "event": {
                        "eventId": invite.eventId,
                        "username": invite.username,
                        "status": invite.status.value,
                    }
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


@router.put("")
def update_invite_status(invite: InviteModel):
    """
    Update invite status
    """
    try:
        update_invite(invite.eventId, invite.username, invite.status)
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "event": {
                        "eventId": invite.eventId,
                        "username": invite.username,
                        "status": invite.status.value,
                    }
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


@router.delete("")
def remove_invite(invite: InviteModel):
    """
    Remove invite
    """
    try:
        delete_invite(invite.eventId, invite.username)
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"message": "Invite deleted"}),
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )
