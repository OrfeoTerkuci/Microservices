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
    try:
        response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
        return response.status_code == 200
    except httpx.ConnectError:
        return False


def check_event_exists(eventId: int):
    try:
        response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
        return response.status_code == 200
    except httpx.ConnectError:
        return False


@router.get(
    "",
    summary="Get invites",
    description="""Get invites by user and event ID. 
    If no parameters are provided, all invites will be returned. 
    If only one parameter is provided, 
    invites will be filtered by that parameter.""",
    responses={
        200: {
            "description": "Invites",
            "content": {
                "application/json": {
                    "example": {
                        "invites": [
                            {"eventId": 1, "username": "john_doe", "status": "YES"}
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Invite not found",
            "content": {"application/json": {"example": {"error": "Invite not found"}}},
        },
    },
)
async def get_invite(
    username: str = Query(default=None, description="User's username"),
    eventId: int = Query(default=None, description="Event's ID"),
):
    params = {}
    if username:
        params["username"] = username
    if eventId:
        params["eventId"] = eventId
    try:
        response = httpx.get("http://invites-service:8000/api/invites", params=params)
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
    summary="Create invite",
    description="Create invite",
    responses={
        201: {
            "description": "Invite created",
            "content": {
                "application/json": {
                    "example": {
                        "event": {
                            "eventId": 1,
                            "username": "john_doe",
                            "status": "YES",
                        }
                    }
                }
            },
        },
        404: {
            "description": "User or event not found",
            "content": {"application/json": {"example": {"error": "User not found"}}},
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def create_invite(invite: InviteModel):
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
    try:
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
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.put(
    "",
    summary="Update invite",
    description="Update invite",
    responses={
        200: {
            "description": "Invite updated",
            "content": {
                "application/json": {
                    "example": {
                        "event": {
                            "eventId": 1,
                            "username": "john_doe",
                            "status": "YES",
                        }
                    }
                }
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
async def update_invite(invite: InviteModel):
    try:
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
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )


@router.delete(
    "/{eventId}/{username}",
    summary="Delete invite",
    description="Delete invite",
    responses={
        200: {
            "description": "Invite deleted",
            "content": {"application/json": {"example": {"message": "Invite deleted"}}},
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def delete_invite(eventId: int, username: str):
    try:
        response = httpx.delete(
            f"http://invites-service:8000/api/invites/{eventId}/{username}",
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