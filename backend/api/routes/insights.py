"""Insight analytics endpoints.

Exposes portfolio-level analytics: overview stats, risk segments,
transaction patterns, repayment distribution, and betting correlation.
"""

import json
import logging

import duckdb
from fastapi import APIRouter, HTTPException

from backend.core.config import ARTIFACTS_DIR
from backend.models.schemas import (
    FeatureImportanceResponse,
    OverviewResponse,
)
from backend.services.analytics import (
    get_betting_correlation,
    get_overview,
    get_repayment_distribution,
    get_risk_segments,
    get_transaction_patterns,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/overview", response_model=OverviewResponse)
def overview() -> dict:
    """Return high-level portfolio statistics."""
    try:
        return get_overview()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/features", response_model=FeatureImportanceResponse)
def feature_importance() -> dict:
    """Return feature importance from the most recently trained model."""
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=503, detail="Model not trained yet.")
    try:
        data = json.loads(metrics_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read metrics file: %s", exc)
        raise HTTPException(status_code=500, detail="Corrupted metrics file.") from exc
    return {
        "feature_importance": data["feature_importance"],
        "model": data["best_model"],
        "auc": data["full_auc"],
    }


@router.get("/segments")
def risk_segments() -> list[dict]:
    """Return borrower counts and default rates by risk segment."""
    try:
        return get_risk_segments()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/transactions")
def transaction_patterns() -> dict:
    """Return monthly flows, categories, and hourly distribution."""
    try:
        return get_transaction_patterns()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/repayment")
def repayment_distribution() -> list[dict]:
    """Return borrower counts and average loans by repayment status."""
    try:
        return get_repayment_distribution()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


@router.get("/betting")
def betting_correlation() -> list[dict]:
    """Return per-borrower betting spend ratio and default status."""
    try:
        return get_betting_correlation()
    except duckdb.IOException as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
