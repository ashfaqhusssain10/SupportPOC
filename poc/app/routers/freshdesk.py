from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.database import get_db
from app.models.incidence import Incidence
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/freshdesk/sidebar", response_class=HTMLResponse)
async def get_freshdesk_sidebar(
    email: str = Query(None),
    phone: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # Determine User ID from email or phone (In a real app, logic would be more complex)
    # For POC, we treat the email as the user_id or part of it
    user_identifier = email or phone or "unknown"
    
    # 1. Fetch Latest Incidence for this User
    # We strip 'freshdesk_' prefix if present, or just fuzzy match? 
    # For this POC, let's look for the most recent incidence that matches user_id partial or exact
    
    # Simple Logic: Search by user_id
    query = (
        select(Incidence)
        .where(Incidence.user_id == user_identifier)
        .order_by(Incidence.created_at.desc())
        .limit(1)
    )
    result = await db.execute(query)
    incidence = result.scalar_one_or_none()
    
    # Mock Data if no incidence found (so sidebar always looks good)
    if not incidence:
        # Fallback: Just get the absolute latest incidence for demo purposes
        # query = select(Incidence).order_by(Incidence.created_at.desc()).limit(1)
        # result = await db.execute(query)
        # incidence = result.scalar_one_or_none()
        pass

    # Extract Data for Template
    data = {
        "friction_score": incidence.friction_score if incidence else 0,
        "cart_value": incidence.cart_value if incidence else 0,
        "item_count": 3, # Mock item count or derive from cart
        "stage": incidence.stage if incidence else "Unknown",
        "last_active": "Just now" if incidence else "Never",
        "email": email or "Guest"
    }

    # Generate HTML (Inline for simplicity, or load template file)
    # Using inline f-string for zero-dependency speed
    
    FRICTION_COLOR = "#ef4444" if data["friction_score"] > 5 else "#22c55e"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 12px; margin: 0; background: #f8fafc; }}
            .card {{ background: white; border-radius: 8px; border: 1px solid #e2e8f0; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
            .title {{ font-size: 14px; font-weight: 600; color: #64748b; }}
            .score {{ font-size: 24px; font-weight: 700; color: {FRICTION_COLOR}; }}
            .score-label {{ font-size: 11px; color: #64748b; font-weight: 500; }}
            
            .metric-row {{ display: flex; gap: 12px; margin-bottom: 16px; }}
            .metric {{ flex: 1; background: #f1f5f9; padding: 8px; border-radius: 6px; text-align: center; }}
            .metric-val {{ font-size: 16px; font-weight: 600; color: #0f172a; }}
            .metric-key {{ font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
            
            .timeline {{ margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 12px; }}
            .timeline-item {{ display: flex; gap: 8px; margin-bottom: 10px; font-size: 12px; }}
            .time {{ color: #94a3b8; min-width: 45px; }}
            .event {{ color: #334155; }}
            
            .btn {{ display: block; width: 100%; padding: 8px; background: #2563eb; color: white; text-align: center; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; margin-top: 12px; }}
            .btn:hover {{ background: #1d4ed8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div>
                    <div class="title">FRICTION SCORE</div>
                    <div class="score-label">Live Analysis</div>
                </div>
                <div class="score">{data['friction_score']}</div>
            </div>
            
            <div class="metric-row">
                <div class="metric">
                    <div class="metric-val">₹{data['cart_value']}</div>
                    <div class="metric-key">Cart Value</div>
                </div>
                 <div class="metric">
                    <div class="metric-val">{data['item_count']}</div>
                    <div class="metric-key">Items</div>
                </div>
            </div>
            
            <div class="timeline">
                <div class="title" style="margin-bottom:8px">RECENT ACTIVITY</div>
                <div class="timeline-item">
                    <span class="time">Now</span>
                    <span class="event">Looking at Menu</span>
                </div>
                <div class="timeline-item">
                    <span class="time">5m</span>
                    <span class="event">Added Biryani Platter</span>
                </div>
                <div class="timeline-item">
                    <span class="time">12m</span>
                    <span class="event">Payment Failed (UPI)</span>
                </div>
            </div>
            
            <a href="http://localhost:8000/agent" target="_blank" class="btn">
                Open Admin Console ↗
            </a>
        </div>
    </body>
    </html>
    """
    return html_content
