"""Database connection management for DuckDB.

Provides a single, reusable context manager for obtaining read-only
DuckDB connections. All database access across the application should
go through this module to ensure connections are properly closed.
"""

from contextlib import contextmanager
from typing import Generator

import duckdb

from backend.core.config import DB_PATH


@contextmanager
def get_connection(*, read_only: bool = True) -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Yield a DuckDB connection that is guaranteed to close on exit.

    Args:
        read_only: Whether to open the database in read-only mode.
                   Defaults to True for safety in query-only services.

    Yields:
        A DuckDB connection bound to the configured database path.
    """
    conn = duckdb.connect(str(DB_PATH), read_only=read_only)
    try:
        yield conn
    finally:
        conn.close()
