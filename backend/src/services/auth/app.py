"""
This file contains the security routes for the FastAPI application.
"""

import auth
import users
from fastapi import FastAPI

app = FastAPI(
    title="Authentication Service API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    root_path="/api",
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
