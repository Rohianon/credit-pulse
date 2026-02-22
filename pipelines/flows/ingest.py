import duckdb

from backend.core.config import DATA_DIR, DB_PATH

SOURCES = [
    ("mpesa_statements.csv", "raw_mpesa_transactions", "read_csv_auto"),
    ("loan_repayment_data.csv", "raw_loan_repayments", "read_csv_auto"),
]


def _ingest_table(con: duckdb.DuckDBPyConnection, filename: str, table: str, reader: str):
    path = DATA_DIR / filename
    if not path.exists():
        return
    con.execute(f"DROP TABLE IF EXISTS {table}")
    con.execute(f"CREATE TABLE {table} AS SELECT * FROM {reader}('{path}', nullstr='NA', sample_size=-1)")
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"Ingested {count:,} rows into {table}")


def _ingest_xlsx(con: duckdb.DuckDBPyConnection):
    path = DATA_DIR / "sql_extract.xlsx"
    if not path.exists():
        return
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("DROP TABLE IF EXISTS raw_sql_extract")
    con.execute(f"CREATE TABLE raw_sql_extract AS SELECT * FROM st_read('{path}')")
    count = con.execute("SELECT COUNT(*) FROM raw_sql_extract").fetchone()[0]
    print(f"Ingested {count:,} rows into raw_sql_extract")


def ingest_data():
    con = duckdb.connect(str(DB_PATH))
    for filename, table, reader in SOURCES:
        _ingest_table(con, filename, table, reader)
    _ingest_xlsx(con)
    con.close()
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    ingest_data()
