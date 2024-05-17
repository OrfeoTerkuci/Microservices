import json

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field
from wrapper import (
    create_response,
    delete_response,
    find_all_responses,
    find_response,
    find_response_by_event,
    find_responses_by_user,
    RSVP_STATUS,
    update_response,
)

router = APIRouter()


class RsvpResponseModel(BaseModel):
    eventId: int = Field(..., description="Event's ID")
    username: str = Field(..., min_length=1, description="User's username")
    status: RSVP_STATUS = Field(..., description="Response status")


@router.get("")
def get_response(
    username: str = Query(default=None, description="User's username"),
    eventId: int = Query(default=None, description="Event's ID"),
):
    """
    Get response by user and event ID
    """
    if username and eventId:
        response = find_response(eventId, username)
        if not response:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error": "Response not found"}),
                media_type="application/json",
            )
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {
                    "response": {
                        "eventId": response.eventId,
                        "username": response.username,
                        "status": response.status,
                    }
                }
            ),
            media_type="application/json",
        )
    elif username:
        responses = find_responses_by_user(username)
    elif eventId:
        responses = find_response_by_event(eventId)
    else:
        responses = find_all_responses()
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "responses": [
                    {
                        "eventId": response.eventId,
                        "username": response.username,
                        "status": response.status,
                    }
                    for response in responses
                ]
            }
        ),
        media_type="application/json",
    )


@router.post("")
def create_rsvp(response: RsvpResponseModel):
    """
    Create a new response
    """
    try:
        create_response(response.eventId, response.username, response.status)
    except Exception as exc:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(exc)}),
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=json.dumps(
            {
                "response": {
                    "eventId": response.eventId,
                    "username": response.username,
                    "status": response.status.value,
                }
            }
        ),
        media_type="application/json",
    )


@router.put("")
def update_rsvp(response: RsvpResponseModel):
    """
    Update a response
    """
    try:
        update_response(response.eventId, response.username, response.status)
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
                "response": {
                    "eventId": response.eventId,
                    "username": response.username,
                    "status": response.status.value,
                }
            }
        ),
        media_type="application/json",
    )


@router.delete("/{eventId}/{username}")
def delete_rsvp(eventId: int, username: str):
    """
    Delete a response
    """

    try:
        delete_response(eventId, username)
    except Exception as exc:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"error": str(exc)}),
            media_type="application/json",
        )
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"message": "Response deleted"}),
        media_type="application/json",
    )
