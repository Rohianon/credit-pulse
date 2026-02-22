"""Credit Pulse application entry point.

Creates the FastAPI application, registers middleware and routers,
and optionally serves the frontend static build if present.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import health, insights, scoring, sql_analysis
from backend.core.config import DB_PATH

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Validate critical resources on startup, clean up on shutdown."""
    if not DB_PATH.exists():
        logger.warning(
            "Database not found at %s. Run the data pipeline before querying.", DB_PATH
        )
    else:
        logger.info("Database found at %s", DB_PATH)
    yield


app = FastAPI(
    title="Credit Pulse",
    description="Credit risk scoring platform for M-Pesa transaction data",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that prevents raw stack traces from leaking to clients."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(health.router)
app.include_router(scoring.router)
app.include_router(insights.router)
app.include_router(sql_analysis.router)

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
