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


@router.get("")
async def get_events():
    """
    Get events.
    """
    response = httpx.get("http://events-service:8000/api/events")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.get("/public")
async def get_public_events():
    """
    Get public events.
    """
    response = httpx.get("http://events-service:8000/api/events/public")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.get("/{eventId}")
async def get_event(eventId: int):
    """
    Get event by ID.
    """
    response = httpx.get(f"http://events-service:8000/api/events/{eventId}")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )


@router.post("")
async def create_event(event: EventModel):
    # Check if the organizer is valid

    response = httpx.get(
        f"http://auth-service:8000/api/users?username={event.organizer}"
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


@router.put("/{eventId}")
async def modify_event(eventId: int, event: EventModel):
    """
    Update an event by its id.
    """
    response = httpx.get(
        f"http://auth-service:8000/api/users?username={event.organizer}"
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


@router.delete("/{eventId}")
async def delete_event(eventId: int):
    """
    Delete an event by its id.
    """
    response = httpx.delete(f"http://events-service:8000/api/events/{eventId}")
    return Response(
        status_code=response.status_code,
        content=response.content,
        media_type="application/json",
    )
