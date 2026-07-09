"""
API Versioning utilities for Convocatoria AI Engine.
Provides clean version management and OpenAPI documentation.
"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel


class APIVersion(BaseModel):
    """API Version metadata."""

    version: str
    release_date: str
    breaking_changes: bool = False
    deprecation_date: str | None = None


# Version registry
API_VERSIONS: dict[str, APIVersion] = {
    "v1": APIVersion(version="v1", release_date="2026-01-01", breaking_changes=False),
    "v2": APIVersion(version="v2", release_date="2026-07-01", breaking_changes=True),
}


def create_versioned_router(prefix: str = "/api/v1", **kwargs) -> APIRouter:
    """Create a versioned API router with standard configuration."""
    router = APIRouter(prefix=prefix, **kwargs)
    return router


def add_version_headers(response: dict[str, Any], version: str = "v1") -> dict[str, Any]:
    """Add version headers to API responses."""
    response["_version"] = {"api_version": version, "supported_versions": list(API_VERSIONS.keys())}
    return response


class VersionedResponse(BaseModel):
    """Base model for versioned API responses."""

    data: Any
    _version: str = "v1"
    _links: dict[str, str] | None = None


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    code: str
    details: Any | None = None
    request_id: str | None = None


# OpenAPI examples
OPENAPI_EXAMPLES = {
    "convocatoria_create": {
        "summary": "Create convocatoria event",
        "description": "Creates a calendar event with notification",
        "value": {
            "title": "Reunion de Planificacion Q3",
            "start_datetime": "2026-07-15T14:00:00-05:00",
            "attendees": ["ana@example.com", "carlos@example.com"],
        },
    },
    "convocatoria_response": {
        "summary": "Convocatoria creation response",
        "value": {
            "event": {"success": True, "event_id": "abc123", "link": "https://..."},
            "notifications": [{"success": True}],
            "report": {"success": True},
        },
    },
}


def get_openapi_schema() -> dict[str, Any]:
    """Generate OpenAPI schema for documentation."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Convocatoria AI Engine API",
            "version": "1.0.0",
            "description": "API for automated convocatoria generation and management",
        },
        "paths": {
            "/api/v1/convocatoria": {
                "post": {
                    "summary": "Create convocatoria",
                    "requestBody": {
                        "content": {"application/json": {"examples": OPENAPI_EXAMPLES}}
                    },
                }
            }
        },
    }
