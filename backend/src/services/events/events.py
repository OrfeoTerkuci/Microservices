import json
from pydantic import BaseModel
from fastapi import APIRouter, Response, status
from wrapper import (
    create_event,
    delete_event,
    find_all_events,
    find_event,
    update_event,
)
import httpx
router = APIRouter()

class EventModel(BaseModel):
    title: str
    description: str
    date: str
    organizerId: int
    isPublic: bool


@router.get("/")
async def get_events():
    """
    Get events.
    """
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=[json.dumps({"events": [event for event in find_all_events()]})],
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )

@router.get("/{event_id}")
async def get_event(event_id: int):
    """
    Get an event by its id.
    """
    try:
        event = find_event(event_id)
        if not event:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Event not found"}),
                media_type="application/json",
            )
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"event": event}),
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )
    
@router.post("/")
async def add_event(event: EventModel):
    """
    Create an event.
    """
    # Check if the organizerId is valid
    try:
        response = httpx.get(f"http://auth-service:8000/api/users/{event.organizerId}")
        if response.status_code != 200:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Organizer not found"}),
                media_type="application/json",
            )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps({"event": create_event(
                title=event.title,
                description=event.description,
                date=event.date,
                organizerId=event.organizerId,
                isPublic=event.isPublic,
            )}),
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )