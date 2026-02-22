import json

from fastapi import APIRouter, HTTPException

from backend.core.config import ARTIFACTS_DIR
from backend.services.analytics import (
    get_betting_correlation,
    get_overview,
    get_repayment_distribution,
    get_risk_segments,
    get_transaction_patterns,
)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/overview")
def overview():
    return get_overview()


@router.get("/features")
def feature_importance():
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=503, detail="Model not trained yet.")
    data = json.loads(metrics_path.read_text())
    return {
        "feature_importance": data["feature_importance"],
        "model": data["best_model"],
        "auc": data["full_auc"],
    }


@router.get("/segments")
def risk_segments():
    return get_risk_segments()


@router.get("/transactions")
def transaction_patterns():
    return get_transaction_patterns()


@router.get("/repayment")
def repayment_distribution():
    return get_repayment_distribution()


@router.get("/betting")
def betting_correlation():
    return get_betting_correlation()
