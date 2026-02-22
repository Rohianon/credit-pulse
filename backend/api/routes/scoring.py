from fastapi import APIRouter, HTTPException

from backend.models.schemas import ScoreRequest, ScoreResponse
from backend.services.credit_model import predict_risk

router = APIRouter(prefix="/api", tags=["scoring"])


@router.post("/score", response_model=ScoreResponse)
def score_borrower(request: ScoreRequest):
    try:
        return predict_risk(request.model_dump())
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run `make train` first.")
