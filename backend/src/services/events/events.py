import datetime
import json

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from wrapper import (
    create_event,
    delete_event,
    find_all_events,
    find_event,
    update_event,
)

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
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "events": [
                        {
                            "id": event.id,
                            "title": event.title,
                            "description": event.description,
                            "date": event.date,
                            "organizer": event.organizer,
                            "isPublic": event.isPublic,
                        }
                        for event in find_all_events()
                    ]
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


@router.get("/public")
async def get_public_events():
    """
    Get public events.
    """
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "events": [
                        {
                            "id": event.id,
                            "title": event.title,
                            "description": event.description,
                            "date": event.date,
                            "organizer": event.organizer,
                            "isPublic": event.isPublic,
                        }
                        for event in find_all_events()
                        if event.isPublic
                    ]
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
            content=json.dumps(
                {
                    "event": {
                        "id": event.id,
                        "title": event.title,
                        "description": event.description,
                        "date": event.date,
                        "organizer": event.organizer,
                        "isPublic": event.isPublic,
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


@router.post("")
async def add_event(event: EventModel):
    """
    Create an event.
    """
    try:
        created_event = create_event(
            title=event.title,
            description=event.description,
            date=event.date,
            organizer=event.organizer,
            isPublic=event.isPublic,
        )
        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps(
                {
                    "event": {
                        "id": created_event.id,
                        "title": created_event.title,
                        "description": created_event.description,
                        "date": created_event.date,
                        "organizer": created_event.organizer,
                        "isPublic": created_event.isPublic,
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


@router.delete("/{event_id}")
async def remove_event(event_id: int):
    """
    Delete an event by its id.
    """
    try:
        event = find_event(event_id)
        if not event:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Event not found"}),
                media_type="application/json",
            )
        delete_event(event_id)
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"message": "Event deleted"}),
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
        )


@router.put("/{event_id}")
async def modify_event(event_id: int, event: EventModel):
    """
    Update an event by its id.
    """
    try:
        existing_event = find_event(event_id)
        if not existing_event:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Event not found"}),
                media_type="application/json",
            )
        update_event(
            event_id=event_id,
            title=event.title,
            description=event.description,
            date=event.date,
            organizer=event.organizer,
            isPublic=event.isPublic,
        )
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "event": {
                        "id": event_id,
                        "title": event.title,
                        "description": event.description,
                        "date": str(event.date),
                        "organizer": event.organizer,
                        "isPublic": event.isPublic,
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
