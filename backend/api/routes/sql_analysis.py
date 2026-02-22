"""SQL extract analysis endpoints.

Exposes analytical queries over the raw_sql_extract table, providing
record counts, per-user latest records, top users, and daily trends.
"""

import duckdb
from fastapi import APIRouter, HTTPException

from backend.models.schemas import SqlTotalResponse
from backend.services.sql_extract import (
    get_latest_per_user,
    get_records_per_day,
    get_top_users,
    get_total_records,
)

router = APIRouter(prefix="/api/sql", tags=["sql-analysis"])


@router.get("/total", response_model=SqlTotalResponse)
def total_records() -> dict:
    """Return total record count and distinct users."""
    try:
        return get_total_records()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/latest-per-user")
def latest_per_user() -> list[dict]:
    """Return the most recent record for each user."""
    try:
        return get_latest_per_user()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/top-users")
def top_users() -> list[dict]:
    """Return the top 5 users by record count."""
    try:
        return get_top_users()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/records-per-day")
def records_per_day() -> list[dict]:
    """Return daily record counts in chronological order."""
    try:
        return get_records_per_day()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
