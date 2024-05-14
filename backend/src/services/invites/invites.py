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
    INVITE_STATUS,
    update_invite,
)

router = APIRouter()


class InviteModel(BaseModel):
    eventId: str
    username: str
    status: INVITE_STATUS


@router.get("")
def get_invite(
    username: str = Query(default=None, description="User's username"),
    eventId: str = Query(default=None, description="Event's ID"),
):
    """
    Get invite by user and event ID
    """
    if not (username and eventId):
        invites = find_all_invites()
        return Response(
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
    # check if the user and event exist

    response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
    if response.status_code != 200:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "User not found"}),
            media_type="application/json",
        )
    response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
    if response.status_code != 200:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Event not found"}),
            media_type="application/json",
        )
    try:
        invite = find_invite(eventId, username)
        if not invite:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Invite not found"}),
                media_type="application/json",
            )
        return Response(
            content=json.dumps(
                {
                    "eventId": invite.eventId,
                    "username": invite.username,
                    "status": invite.status,
                }
            ),
            media_type="application/json",
        )
    except Exception as exc:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(exc)}),
            media_type="application/json",
        )


@router.post("")
def add_invite(invite: InviteModel):
    """
    Create invite
    """
    try:
        # check if the user and event exist

        response = httpx.get(
            f"http://auth-service:8000/api/users?username={invite.username}"
        )
        if response.status_code != 200:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "User not found"}),
                media_type="application/json",
            )
        response = httpx.get(f"http://events-service:8000/api/events/{invite.eventId}")
        if response.status_code != 200:
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
                        "status": invite.status,
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
        # Check if user and event still exist

        response = httpx.get(
            f"http://auth-service:8000/api/users?username={invite.username}"
        )
        if response.status_code != 200:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "User not found"}),
                media_type="application/json",
            )
        response = httpx.get(f"http://events-service:8000/api/events/{invite.eventId}")
        if response.status_code != 200:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Event not found"}),
                media_type="application/json",
            )
        update_invite(invite.eventId, invite.username, invite.status)
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "event": {
                        "eventId": invite.eventId,
                        "username": invite.username,
                        "status": invite.status,
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
