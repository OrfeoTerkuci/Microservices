"""
This file contains the event routes for the FastAPI application.
"""

import invites
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Invites Service API",
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


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(invites.router, prefix="/invites", tags=["invites"])
