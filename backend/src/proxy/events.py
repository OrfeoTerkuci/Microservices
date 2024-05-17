import datetime
import json

import httpx

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

router = APIRouter()


class EventModel(BaseModel):
    title: str
    description: str
    date: datetime.date = Field(..., description="Date in YYYY-MM-DD format")
    organizer: str
    isPublic: bool


@router.get(
    "",
    summary="Get all events",
    description="Get all events.",
    responses={
        200: {
            "description": "All the events",
            "content": {
                "application/json": {
                    "example": {
                        "events": [
                            {
                                "id": 1,
                                "title": "Independence!!!",
                                "description": "Chase those Ottomans (not the couches) away!",
                                "date": "1912-11-28",
                                "organizer": "Ismail Qemali",
                                "isPublic": True,
                            }
                        ]
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
async def get_events():
    """
    Get events.
    """
    try:
        response = httpx.get("http://events-service:8000/api/events")
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
    "/public",
    summary="Get all public events",
    description="Get all public events.",
    responses={
        200: {
            "description": "All the public events",
            "content": {
                "application/json": {
                    "example": {
                        "events": [
                            {
                                "id": 1,
                                "title": "Independence!!!",
                                "description": "Chase those Ottomans (not the couches) away!",
                                "date": "1912-11-28",
                                "organizer": "Ismail Qemali",
                                "isPublic": True,
                            }
                        ]
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
async def get_public_events():
    """
    Get public events.
    """
    try:
        response = httpx.get("http://events-service:8000/api/events/public")
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
    "/{eventId}",
    summary="Get event by ID",
    description="Get event by ID.",
    responses={
        200: {
            "description": "The event",
            "content": {
                "application/json": {
                    "example": {
                        "event": {
                            "id": 1,
                            "title": "Independence!!!",
                            "description": "Chase those Ottomans (not the couches) away!",
                            "date": "1912-11-28",
                            "organizer": "Ismail Qemali",
                            "isPublic": True,
                        }
                    }
                }
            },
        },
        404: {
            "description": "Event not found",
            "content": {"application/json": {"example": {"error": "Event not found"}}},
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def get_event(eventId: int):
    """
    Get event by ID.
    """
    try:
        response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
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
    summary="Create an event",
    description="Create an event.",
    responses={
        201: {
            "description": "Event created",
            "content": {
                "application/json": {
                    "example": {
                        "event": {
                            "id": 1,
                            "title": "Independence!!!",
                            "description": "Chase those Ottomans (not the couches) away!",
                            "date": "1912-11-28",
                            "organizer": "Ismail Qemali",
                            "isPublic": True,
                        }
                    }
                }
            },
        },
        404: {
            "description": "Organizer not found",
            "content": {
                "application/json": {"example": {"error": "Organizer not found"}}
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
async def create_event(event: EventModel):
    # Check if the organizer is valid

    try:
        response = httpx.get(
            f"http://auth-service:8000/api/users?username={event.organizer}"
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )
    if response.status_code == 200:
        response = httpx.post(
            "http://events-service:8000/api/events",
            json={
                "title": event.title,
                "description": event.description,
                "date": str(event.date),
                "organizer": event.organizer,
                "isPublic": event.isPublic,
            },
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json.dumps({"error": "Organizer not found"}),
        media_type="application/json",
    )


@router.put(
    "/{eventId}",
    summary="Update an event by ID",
    description="Update an event by ID.",
    responses={
        200: {
            "description": "Event updated",
            "content": {
                "application/json": {
                    "example": {
                        "event": {
                            "id": 1,
                            "title": "Independence!!!",
                            "description": "Chase those Ottomans (not the couches) away!",
                            "date": "1912-11-28",
                            "organizer": "Ismail Qemali",
                            "isPublic": True,
                        }
                    }
                }
            },
        },
        404: {
            "description": "Organizer not found",
            "content": {
                "application/json": {"example": {"error": "Organizer not found"}}
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
async def modify_event(eventId: int, event: EventModel):
    """
    Update an event by its id.
    """
    try:
        response = httpx.get(
            f"http://auth-service:8000/api/users?username={event.organizer}"
        )
    except httpx.ConnectError:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
        )
    if response.status_code == 200:
        response = httpx.put(
            f"http://events-service:8000/api/events/{eventId}",
            json={
                "title": event.title,
                "description": event.description,
                "date": str(event.date),
                "organizer": event.organizer,
                "isPublic": event.isPublic,
            },
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json.dumps({"error": "Organizer not found"}),
        media_type="application/json",
    )


@router.delete(
    "/{eventId}",
    summary="Delete an event by ID",
    description="Delete an event by ID.",
    responses={
        200: {
            "description": "Event deleted",
            "content": {"application/json": {"example": {"message": "Event deleted"}}},
        },
        404: {
            "description": "Event not found",
            "content": {"application/json": {"example": {"error": "Event not found"}}},
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"error": "Internal server error"}}
            },
        },
    },
)
async def delete_event(eventId: int):
    """
    Delete an event by its id.
    """
    try:
        response = httpx.delete(f"http://events-service:8000/api/events/{eventId}")
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
