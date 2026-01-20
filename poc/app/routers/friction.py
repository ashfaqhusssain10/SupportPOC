"""
Friction Detection API - Calculate friction scores.
"""

from fastapi import APIRouter
from app.services.friction_service import FrictionService
from app.schemas.context import FrictionDetectRequest, FrictionDetectResponse

router = APIRouter(prefix="/api/v1/friction", tags=["Friction Detection"])

friction_service = FrictionService()


@router.post("/detect", response_model=FrictionDetectResponse)
async def detect_friction(request: FrictionDetectRequest):
    """
    Calculate friction score from user behavior signals.
    Called when user initiates chat option.
    
    Returns score (0-100), help recommendation, and breakdown.
    """
    return friction_service.calculate_score(request)


@router.get("/thresholds")
async def get_thresholds():
    """Get current friction detection thresholds and weights."""
    return {
        "weights": friction_service.WEIGHTS,
        "thresholds": friction_service.THRESHOLDS,
        "trigger_threshold": 50,
        "high_value_events": friction_service.HIGH_VALUE_EVENTS,
        "help_messages": friction_service.HELP_MESSAGES
    }


@router.post("/interpret")
async def interpret_score(score: float):
    """Get human-readable interpretation of friction score."""
    return {
        "score": score,
        "interpretation": friction_service.get_score_interpretation(score),
        "should_show_help": score >= 50
    }
