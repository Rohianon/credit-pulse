"""Credit portfolio insight analytics.

Provides read-only analytical queries against the credit feature mart
and M-Pesa transaction staging tables. Each function returns a
dictionary (or list of dicts) ready for JSON serialization.

This module is responsible only for insight-level analytics
(overview, segments, transaction patterns, betting correlation,
repayment distribution). SQL extract queries live in sql_extract.py.
"""

from backend.core.database import get_connection


def _to_native(row: dict) -> dict:
    """Convert DuckDB numeric types to Python floats for JSON serialization."""
    return {k: float(v) if v is not None else 0.0 for k, v in row.items()}


def get_overview() -> dict:
    """Return high-level portfolio statistics (borrower count, default rate, etc.)."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*)              AS total_borrowers,
                SUM(is_defaulted)     AS total_defaults,
                AVG(is_defaulted)     AS default_rate,
                AVG(loan_amount)      AS avg_loan_amount,
                SUM(loan_amount)      AS total_disbursed,
                AVG(repayment_ratio)  AS avg_repayment_ratio
            FROM mart_credit_features
        """).fetchdf().to_dict(orient="records")[0]
    return _to_native(row)


def get_risk_segments() -> list[dict]:
    """Return default rate and average loan by risk segment."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                risk_segment,
                COUNT(*)  AS count,
                AVG(CASE WHEN is_defaulted = 1 THEN 1.0 ELSE 0.0 END) AS default_rate,
                AVG(loan_amount) AS avg_loan
            FROM mart_risk_segments
            GROUP BY risk_segment
            ORDER BY risk_segment
        """).fetchdf().to_dict(orient="records")


def get_transaction_patterns() -> dict:
    """Return monthly flows, category breakdown, and hourly distribution."""
    with get_connection() as conn:
        monthly = conn.execute("""
            SELECT
                date_trunc('month', transaction_at) AS month,
                SUM(received_amount)                AS total_inflows,
                SUM(sent_amount)                    AS total_outflows,
                COUNT(*)                            AS tx_count
            FROM stg_mpesa_transactions
            GROUP BY date_trunc('month', transaction_at)
            ORDER BY month
        """).fetchdf()
        monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

        categories = conn.execute("""
            SELECT
                tx_category,
                COUNT(*)          AS count,
                SUM(sent_amount)  AS total_amount
            FROM stg_mpesa_transactions
            GROUP BY tx_category
            ORDER BY total_amount DESC
        """).fetchdf()

        hourly = conn.execute("""
            SELECT
                EXTRACT(hour FROM transaction_at) AS hour,
                COUNT(*)                          AS count
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
    """Return per-borrower betting spend ratio alongside default status."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                customer_id,
                betting_spend_ratio,
                is_defaulted,
                loan_amount
            FROM mart_credit_features
            ORDER BY betting_spend_ratio DESC
        """).fetchdf().to_dict(orient="records")


def get_repayment_distribution() -> list[dict]:
    """Return borrower counts and average loan amounts by repayment status."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                CASE WHEN is_defaulted = 1 THEN 'Defaulted' ELSE 'Repaid' END AS status,
                COUNT(*)          AS count,
                AVG(loan_amount)  AS avg_loan_amount
            FROM mart_credit_features
            GROUP BY is_defaulted
        """).fetchdf().to_dict(orient="records")
