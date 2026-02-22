"""Pydantic models for API request and response validation.

Every route that accepts structured input or returns a well-defined
shape should reference models from this module. This keeps the API
contract explicit and enables automatic OpenAPI documentation.
"""

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class ScoreRequest(BaseModel):
    """Input features for scoring a single borrower."""

    transaction_count: float = 0
    active_days: float = 0
    transaction_frequency: float = 0
    total_inflows: float = 0
    total_outflows: float = 0
    inflow_outflow_ratio: float = 0
    avg_balance: float = 0
    min_balance: float = 0
    max_balance: float = 0
    balance_volatility: float = 0
    avg_received_amount: float = 0
    max_received_amount: float = 0
    spending_consistency: float = 0
    days_since_last_transaction: float = 0
    account_age_days: float = 0
    betting_spend_ratio: float = 0
    utility_payment_ratio: float = 0
    cash_withdrawal_ratio: float = 0
    airtime_spend_ratio: float = 0
    merchant_spend_ratio: float = 0
    p2p_transfer_ratio: float = 0
    loan_product_count: float = 0


class ScoreResponse(BaseModel):
    """Risk assessment result for a single borrower."""

    risk_score: float
    risk_label: str
    default_probability: float
    model_used: str
    top_factors: list[dict]


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

class OverviewResponse(BaseModel):
    """High-level portfolio statistics."""

    total_borrowers: float
    total_defaults: float
    default_rate: float
    avg_loan_amount: float
    total_disbursed: float
    avg_repayment_ratio: float


class FeatureImportanceResponse(BaseModel):
    """Model feature importance with metadata."""

    feature_importance: list
    model: str
    auc: float


class RiskSegmentItem(BaseModel):
    """A single row from the risk segment breakdown."""

    risk_segment: str
    count: int
    default_rate: float
    avg_loan: float


class RepaymentDistributionItem(BaseModel):
    """Borrower count and average loan by repayment status."""

    status: str
    count: int
    avg_loan_amount: float


# ---------------------------------------------------------------------------
# SQL Extract
# ---------------------------------------------------------------------------

class SqlTotalResponse(BaseModel):
    """Total record and distinct user counts from the raw SQL extract."""

    total_records: int
    distinct_users: int
