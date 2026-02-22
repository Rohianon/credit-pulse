from contextlib import contextmanager

import duckdb

from backend.core.config import DB_PATH


@contextmanager
def connection():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        yield con
    finally:
        con.close()


def _to_native(row: dict) -> dict:
    return {k: float(v) if v is not None else 0 for k, v in row.items()}


def get_overview() -> dict:
    with connection() as con:
        row = con.execute("""
            SELECT
                COUNT(*) as total_borrowers,
                SUM(is_defaulted) as total_defaults,
                AVG(is_defaulted) as default_rate,
                AVG(loan_amount) as avg_loan_amount,
                SUM(loan_amount) as total_disbursed,
                AVG(repayment_ratio) as avg_repayment_ratio
            FROM mart_credit_features
        """).fetchdf().to_dict(orient="records")[0]
    return _to_native(row)


def get_risk_segments() -> list[dict]:
    with connection() as con:
        return con.execute("""
            SELECT
                risk_segment,
                COUNT(*) as count,
                AVG(CASE WHEN is_defaulted = 1 THEN 1.0 ELSE 0.0 END) as default_rate,
                AVG(loan_amount) as avg_loan
            FROM mart_risk_segments
            GROUP BY risk_segment
            ORDER BY risk_segment
        """).fetchdf().to_dict(orient="records")


def get_transaction_patterns() -> dict:
    with connection() as con:
        monthly = con.execute("""
            SELECT
                date_trunc('month', transaction_at) as month,
                SUM(received_amount) as total_inflows,
                SUM(sent_amount) as total_outflows,
                COUNT(*) as tx_count
            FROM stg_mpesa_transactions
            GROUP BY date_trunc('month', transaction_at)
            ORDER BY month
        """).fetchdf()
        monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

        categories = con.execute("""
            SELECT
                tx_category,
                COUNT(*) as count,
                SUM(sent_amount) as total_amount
            FROM stg_mpesa_transactions
            GROUP BY tx_category
            ORDER BY total_amount DESC
        """).fetchdf()

        hourly = con.execute("""
            SELECT
                EXTRACT(hour FROM transaction_at) as hour,
                COUNT(*) as count
            FROM stg_mpesa_transactions
            GROUP BY EXTRACT(hour FROM transaction_at)
            ORDER BY hour
        """).fetchdf()

    return {
        "monthly_flows": monthly.to_dict(orient="records"),
        "categories": categories.to_dict(orient="records"),
        "hourly_distribution": hourly.to_dict(orient="records"),
    }


def get_betting_correlation() -> list[dict]:
    with connection() as con:
        return con.execute("""
            SELECT
                customer_id,
                betting_spend_ratio,
                is_defaulted,
                loan_amount
            FROM mart_credit_features
            ORDER BY betting_spend_ratio DESC
        """).fetchdf().to_dict(orient="records")


def get_repayment_distribution() -> list[dict]:
    with connection() as con:
        return con.execute("""
            SELECT
                CASE WHEN is_defaulted = 1 THEN 'Defaulted' ELSE 'Repaid' END as status,
                COUNT(*) as count,
                AVG(loan_amount) as avg_loan_amount
            FROM mart_credit_features
            GROUP BY is_defaulted
        """).fetchdf().to_dict(orient="records")


def sql_total_records() -> dict:
    with connection() as con:
        row = con.execute("""
            SELECT COUNT(*) AS total_records, COUNT(DISTINCT user_id) AS distinct_users
            FROM raw_sql_extract
        """).fetchdf().to_dict(orient="records")[0]
    return {k: int(v) for k, v in row.items()}


def sql_latest_per_user() -> list[dict]:
    with connection() as con:
        df = con.execute("""
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ex_date DESC) AS rn
                FROM raw_sql_extract
            ) WHERE rn = 1
            ORDER BY user_id
        """).fetchdf()
    df = df.drop(columns=["rn"], errors="ignore")
    return df.to_dict(orient="records")


def sql_top_users() -> list[dict]:
    with connection() as con:
        return con.execute("""
            SELECT user_id, COUNT(*) AS record_count
            FROM raw_sql_extract
            GROUP BY user_id
            ORDER BY record_count DESC
            LIMIT 5
        """).fetchdf().to_dict(orient="records")


def sql_records_per_day() -> list[dict]:
    with connection() as con:
        df = con.execute("""
            SELECT CAST(ex_date AS DATE) AS record_date, COUNT(*) AS daily_count
            FROM raw_sql_extract
            GROUP BY CAST(ex_date AS DATE)
            ORDER BY record_date
        """).fetchdf()
    df["record_date"] = df["record_date"].astype(str)
    return df.to_dict(orient="records")
