"""
This is the proxy for the backend services
"""

import auth
import calendars
import events
import invites
import rsvp
import users
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(calendars.router, prefix="/calendars", tags=["calendars"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(invites.router, prefix="/invites", tags=["invites"])
app.include_router(rsvp.router, prefix="/rsvp", tags=["rsvp"])
