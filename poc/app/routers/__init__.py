# Routers package
from app.routers.webhooks import router as webhooks_router
from app.routers.context import router as context_router
from app.routers.incidences import router as incidences_router
from app.routers.channel import router as channel_router
from app.routers.friction import router as friction_router
from app.routers.analytics import router as analytics_router
from app.routers.messages import router as messages_router
from app.routers.call import router as call_router
from app.routers.freshdesk import router as freshdesk_router
from app.routers.freshdesk_sync import router as freshdesk_sync_router
