from fastapi import APIRouter

from backend.services.analytics import (
    sql_latest_per_user,
    sql_records_per_day,
    sql_top_users,
    sql_total_records,
)

router = APIRouter(prefix="/api/sql", tags=["sql-analysis"])


@router.get("/total")
def total_records():
    return sql_total_records()


@router.get("/latest-per-user")
def latest_per_user():
    return sql_latest_per_user()


@router.get("/top-users")
def top_users():
    return sql_top_users()


@router.get("/records-per-day")
def records_per_day():
    return sql_records_per_day()
