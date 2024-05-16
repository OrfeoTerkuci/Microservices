import enum
import json

import httpx
from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field

router = APIRouter()


class RSVP_STATUS(enum.Enum):
    """
    RSVP status enum
    """

    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"


class RsvpResponseModel(BaseModel):
    eventId: int = Field(..., description="Event's ID")
    username: str = Field(..., min_length=1, description="User's username")
    status: RSVP_STATUS = Field(..., description="Response status")


def check_user_exists(username: str):
    response = httpx.get(f"http://auth-service:8000/api/users?username={username}")
    return response.status_code == 200


def check_public_event_exists(eventId: int):
    response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
    return response.status_code == 200 and response.json()["event"]["isPublic"]


@router.get("")
def get_responses(
    username: str = Query(default=None, description="User's username"),
    eventId: int = Query(default=None, description="Event's ID"),
):
    """
    Get all responses
    """
    params = {}
    if username:
        params["username"] = username
    if eventId:
        params["eventId"] = eventId
    response = httpx.get("http://rsvp-service:8000/api/rsvp", params=params)
    return Response(
        status_code=status.HTTP_200_OK,
        content=response.content,
        media_type="application/json",
    )


@router.post("")
def create_response(response: RsvpResponseModel):
    """
    Create response
    """
    # Check if the user and event exist and are public

    if not check_user_exists(response.username):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "User not found"}),
            media_type="application/json",
        )
    if not check_public_event_exists(response.eventId):
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error": "Public event not found"}),
            media_type="application/json",
        )
    result = httpx.post(
        "http://rsvp-service:8000/api/rsvp",
        json={
            "eventId": response.eventId,
            "username": response.username,
            "status": response.status.value,
        },
    )
    return Response(
        status_code=result.status_code,
        content=result.content,
        media_type="application/json",
    )


@router.put("")
def update_response(response: RsvpResponseModel):
    """
    Update response
    """
    result = httpx.put(
        "http://rsvp-service:8000/api/rsvp",
        json={
            "eventId": response.eventId,
            "username": response.username,
            "status": response.status.value,
        },
    )
    return Response(
        status_code=result.status_code,
        content=result.content,
        media_type="application/json",
    )


@router.delete("/{eventId}/{username}")
def delete_response(eventId: int, username: str):
    """
    Delete response
    """
    result = httpx.delete(f"http://rsvp-service:8000/api/rsvp/{eventId}/{username}")
    return Response(
        status_code=result.status_code,
        content=result.content,
        media_type="application/json",
    )
