"""Credit scoring endpoint.

Accepts borrower feature vectors and returns a risk assessment
produced by the trained credit model.
"""

import logging

from fastapi import APIRouter, HTTPException

from backend.models.schemas import ScoreRequest, ScoreResponse
from backend.services.credit_model import predict_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["scoring"])


@router.post("/score", response_model=ScoreResponse)
def score_borrower(request: ScoreRequest) -> dict:
    """Score a single borrower against the trained credit model.

    Raises:
        HTTPException 503: If the model has not been trained yet.
        HTTPException 500: If prediction fails for an unexpected reason.
    """
    try:
        return predict_risk(request.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run `make train` first.",
        ) from exc
    except (ValueError, KeyError) as exc:
        logger.error("Prediction failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Prediction failed due to invalid model state.",
        ) from exc
