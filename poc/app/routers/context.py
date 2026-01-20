"""
Context API - Update user context from mobile app.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import json

from app.database import get_db, get_redis
from app.schemas.context import ContextUpdate, FrictionSignalCreate
from app.models.incidence import FrictionSignal

router = APIRouter(prefix="/api/v1/context", tags=["Context"])


@router.post("/update")
async def update_context(
    context: ContextUpdate,
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Update user context from mobile app.
    Stores in Redis for fast access by agents.
    """
    # Store context in Redis with 30 minute TTL
    key = f"user_context:{context.user_id}"
    
    context_data = context.model_dump(exclude_none=True)
    await redis_client.setex(key, 1800, json.dumps(context_data))  # 30 min TTL
    
    return {
        "status": "updated",
        "user_id": context.user_id,
        "ttl_seconds": 1800
    }


@router.get("/{user_id}")
async def get_context(
    user_id: str,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get current user context from Redis."""
    key = f"user_context:{user_id}"
    data = await redis_client.get(key)
    
    if data:
        return {"user_id": user_id, "context": json.loads(data)}
    return {"user_id": user_id, "context": None}


@router.post("/friction-signal")
async def log_friction_signal(
    signal: FrictionSignalCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Log a friction signal from mobile app.
    Used for analytics and friction score calculation.
    """
    friction_signal = FrictionSignal(
        user_id=signal.user_id,
        session_id=signal.session_id,
        signal_type=signal.signal_type,
        value=signal.value,
        screen=signal.screen
    )
    
    db.add(friction_signal)
    await db.flush()
    
    return {
        "status": "logged",
        "signal_type": signal.signal_type,
        "user_id": signal.user_id
    }
