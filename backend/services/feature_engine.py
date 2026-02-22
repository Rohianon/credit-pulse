"""Feature column definitions for the credit scoring model.

Defines the canonical list of feature columns and the target column
used during training and inference. Any changes to the feature set
must be reflected here so that training and prediction stay in sync.
"""

FEATURE_COLUMNS: list[str] = [
    "transaction_count",
    "active_days",
    "transaction_frequency",
    "total_inflows",
    "total_outflows",
    "inflow_outflow_ratio",
    "avg_balance",
    "min_balance",
    "max_balance",
    "balance_volatility",
    "avg_received_amount",
    "max_received_amount",
    "spending_consistency",
    "days_since_last_transaction",
    "account_age_days",
    "betting_spend_ratio",
    "utility_payment_ratio",
    "cash_withdrawal_ratio",
    "airtime_spend_ratio",
    "merchant_spend_ratio",
    "p2p_transfer_ratio",
    "loan_product_count",
]

TARGET_COLUMN: str = "is_defaulted"
