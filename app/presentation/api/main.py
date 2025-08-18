"""FastAPI application for webapp backend."""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.presentation.api.routers import chats

app = FastAPI(
    title="Moderator Bot API",
    version="1.0.0",
    # Disable automatic redirect for trailing slashes to avoid HTTPS->HTTP redirects
    redirect_slashes=False,
)

# Configure CORS for webapp
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.webapp.url] if hasattr(settings, "webapp") else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Add middleware to handle forwarded headers properly for ngrok/proxy setups
@app.middleware("http")
async def force_https_redirect(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Force HTTPS redirects to use HTTPS scheme when behind proxy."""
    # Check if request came through proxy with HTTPS (ngrok sets this header)
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto == "https":
        # Override scheme to prevent HTTP redirects from FastAPI
        request.scope["scheme"] = "https"

    return await call_next(request)


# Include routers
app.include_router(chats.router, prefix="/api/v1/chats", tags=["chats"])


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}
