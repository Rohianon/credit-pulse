"""SQL extract analytics for raw ingested data.

Provides read-only queries against the raw_sql_extract table, which
contains records ingested from external SQL sources. These are kept
separate from the credit insight analytics (analytics.py) because they
operate on a different data domain and serve a different part of the UI.
"""

from backend.core.database import get_connection


def get_total_records() -> dict:
    """Return the total record count and distinct user count from the raw extract."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*)              AS total_records,
                COUNT(DISTINCT user_id) AS distinct_users
            FROM raw_sql_extract
        """).fetchdf().to_dict(orient="records")[0]
    return {k: int(v) for k, v in row.items()}


def get_latest_per_user() -> list[dict]:
    """Return the most recent record per user, ordered by user_id."""
    with get_connection() as conn:
        df = conn.execute("""
            SELECT * FROM (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ex_date DESC) AS rn
                FROM raw_sql_extract
            ) WHERE rn = 1
            ORDER BY user_id
        """).fetchdf()
    df = df.drop(columns=["rn"], errors="ignore")
    return df.to_dict(orient="records")


def get_top_users(limit: int = 5) -> list[dict]:
    """Return the users with the most records, descending.

    Args:
        limit: Maximum number of users to return. Defaults to 5.
    """
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT user_id, COUNT(*) AS record_count
            FROM raw_sql_extract
            GROUP BY user_id
            ORDER BY record_count DESC
            LIMIT ?
            """,
            [limit],
        ).fetchdf().to_dict(orient="records")


def get_records_per_day() -> list[dict]:
    """Return daily record counts, ordered chronologically."""
    with get_connection() as conn:
        df = conn.execute("""
            SELECT
                CAST(ex_date AS DATE) AS record_date,
                COUNT(*)              AS daily_count
            FROM raw_sql_extract
            GROUP BY CAST(ex_date AS DATE)
            ORDER BY record_date
        """).fetchdf()
    df["record_date"] = df["record_date"].astype(str)
    return df.to_dict(orient="records")
