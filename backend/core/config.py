"""Application configuration and constants.

Centralizes all path definitions, model thresholds, and configuration
values used across the backend. Import from here rather than
hardcoding paths in individual modules.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DB_PATH = BASE_DIR / "credit_pulse.duckdb"
MODEL_PATH = ARTIFACTS_DIR / "credit_model.joblib"

RISK_THRESHOLDS = {
    "high": 0.5,
    "medium": 0.3,
}


def risk_label(score: float) -> str:
    """Map a numeric risk score to a human-readable risk category.

    Returns "high", "medium", or "low" based on the configured
    thresholds in RISK_THRESHOLDS.
    """
    if score > RISK_THRESHOLDS["high"]:
        return "high"
    if score > RISK_THRESHOLDS["medium"]:
        return "medium"
    return "low"
