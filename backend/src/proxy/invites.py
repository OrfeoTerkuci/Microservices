import enum
import json

import httpx
from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel

router = APIRouter()


class INVITE_STATUS(enum.Enum):
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"
    PENDING = "PENDING"


class InviteModel(BaseModel):
    eventId: int
    username: str
    status: INVITE_STATUS


class DeleteInviteModel(BaseModel):
    eventId: int
    username: str


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
    params = {}
    if username:
        params["username"] = username
    if eventId:
        params["eventId"] = eventId
    response = httpx.get("http://invites-service:8000/api/invites", params=params)
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.post("")
def create_invite(invite: InviteModel):
    # Check if user and event exist

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
    # Create invite

    response = httpx.post(
        "http://invites-service:8000/api/invites",
        json={
            "eventId": invite.eventId,
            "username": invite.username,
            "status": invite.status.value,
        },
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.put("")
def update_invite(invite: InviteModel):
    response = httpx.put(
        "http://invites-service:8000/api/invites",
        json={
            "eventId": invite.eventId,
            "username": invite.username,
            "status": invite.status.value,
        },
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.delete("/{eventId}/{username}")
def delete_invite(eventId: int, username: str):
    response = httpx.delete(
        f"http://invites-service:8000/api/invites/{eventId}/{username}",
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )
