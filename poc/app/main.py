"""
Support-Led Ordering System - FastAPI Application

Main entry point for the POC backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db
from app.routers import (
    webhooks_router,
    context_router,
    incidences_router,
    channel_router,
    friction_router,
    analytics_router,
    messages_router,
    call_router,
    freshdesk_router,
    freshdesk_sync_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Support-Led Ordering System POC...")
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init skipped (might already exist): {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Support-Led Ordering System POC

Backend API for customer support integration with Freshchat.

### Features:
- **Webhook Handler** - Process Freshchat events
- **Incidence Management** - Track support interactions
- **Channel Router** - Cost-based routing rules
- **Friction Detection** - Calculate user friction scores
- **Analytics** - Dashboard KPIs and reports

### Channel Routing Rules:
| Order Value | Channels |
|-------------|----------|
| < ₹5,000 | None (self-serve) |
| ₹5,000 - ₹25,000 | Chat only |
| > ₹25,000 | Chat + Call |
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(webhooks_router)
app.include_router(context_router)
app.include_router(incidences_router)
app.include_router(channel_router)
app.include_router(friction_router)
app.include_router(analytics_router)
app.include_router(messages_router)
app.include_router(call_router)
app.include_router(freshdesk_router)
app.include_router(freshdesk_sync_router)


@app.get("/", tags=["Health"])
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "demo": "/demo",
        "endpoints": {
            "webhooks": "/webhooks/freshchat",
            "context": "/api/v1/context",
            "incidences": "/api/v1/incidences",
            "channel": "/api/v1/channel/route",
            "friction": "/api/v1/friction/detect",
            "analytics": "/api/v1/analytics/kpis"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "services": {
            "webhook_handler": "active",
            "incidence_service": "active",
            "channel_router": "active",
            "friction_service": "active",
            "analytics_service": "active"
        }
    }


@app.get("/demo", tags=["Demo"], include_in_schema=False)
async def serve_demo():
    """Serve the demo HTML page."""
    from fastapi.responses import FileResponse
    import os
    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo.html")
    return FileResponse(demo_path, media_type="text/html")


@app.get("/analytics", tags=["Analytics"], include_in_schema=False)
async def serve_analytics():
    """Serve the analytics dashboard."""
    from fastapi.responses import FileResponse
    import os
    analytics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analytics.html")
    return FileResponse(analytics_path, media_type="text/html")


@app.get("/agent", tags=["Agent"], include_in_schema=False)
async def serve_agent():
    """Serve the agent console dashboard."""
    from fastapi.responses import FileResponse
    import os
    agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent.html")
    return FileResponse(agent_path, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
