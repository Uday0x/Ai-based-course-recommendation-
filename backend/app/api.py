# backend/app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.model import load_artifacts, predict_from_interests

router = APIRouter()

# Load model + vectorizer + meta on startup
load_artifacts()

# ------------ Request & Response Models ------------
class InterestsPayload(BaseModel):
    interests: str = Field(
        ...,
        description="Comma-separated interest keywords, e.g. 'nlp, transformers, deep learning'"
    )

class PredictResponse(BaseModel):
    recommended_course: str
    probability: float
    explanation: Dict[str, Any]

# ------------ Main Predict Endpoint ------------
@router.post("/predict", response_model=PredictResponse)
def predict(payload: InterestsPayload):
    """
    This endpoint expects JSON:
    {
        "interests": "python, ml"
    }

    It passes the string to predict_from_interests() which treats it
    as text for CountVectorizer, NOT a dict. This is correct.
    """
    try:
        recommended, prob, explanation = predict_from_interests(payload.interests)
        return {
            "recommended_course": recommended,
            "probability": round(prob, 4),
            "explanation": explanation
        }
    except Exception as e:
        # Return proper HTTP error
        raise HTTPException(status_code=500, detail=str(e))
