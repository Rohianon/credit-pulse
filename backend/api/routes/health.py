"""Health check endpoint.

Provides a simple liveness probe that downstream monitors and load
balancers can use to verify the service is running.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple status indicator."""
    return {"status": "healthy"}
