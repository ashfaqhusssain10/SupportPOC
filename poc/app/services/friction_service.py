"""
Friction Service - Calculates friction score based on user behavior.
"""

from typing import Optional
from app.config import settings
from app.schemas.context import FrictionDetectRequest, FrictionDetectResponse


class FrictionService:
    """
    Monitors user behavior and calculates friction score.
    Score is calculated when user initiates chat option.
    
    Friction Weights:
    - Inactivity on checkout (>60s): 30 points
    - Back navigation loops (>3): 25 points
    - Excessive price checking (>5): 20 points
    - High-value event: 15 points
    - First-time user: 10 points
    - Payment failures: 40 points
    """
    
    # Signal weights
    WEIGHTS = {
        "inactivity": 30,      # Triggered when >60s inactive
        "back_nav": 25,        # Triggered when >3 back navigations
        "price_check": 20,     # Triggered when >5 price checks
        "high_value_event": 15,
        "first_time_user": 10,
        "payment_failure": 40,
    }
    
    # Thresholds for triggering signals
    THRESHOLDS = {
        "inactivity_seconds": 60,
        "back_nav_count": 3,
        "price_check_count": 5,
        "payment_retry_count": 1,
    }
    
    # High-value event types
    HIGH_VALUE_EVENTS = ["WEDDING", "CORPORATE", "RELIGIOUS", "GOVERNMENT"]
    
    # Suggested help messages based on context
    HELP_MESSAGES = {
        "checkout": "Need help completing your order?",
        "menu": "Can we help you choose the right package?",
        "payment": "Having trouble with payment?",
        "customization": "Let us help you customize your menu",
        "default": "Need assistance? We're here to help!",
    }
    
    def calculate_score(self, request: FrictionDetectRequest) -> FrictionDetectResponse:
        """
        Calculate friction score from user context.
        Called when user opts for chat option.
        
        Args:
            request: Friction detection request with behavior signals
            
        Returns:
            FrictionDetectResponse with score, breakdown, and help recommendation
        """
        score = 0
        breakdown = {}
        
        # Check inactivity
        if request.inactivity_seconds > self.THRESHOLDS["inactivity_seconds"]:
            points = self.WEIGHTS["inactivity"]
            score += points
            breakdown["inactivity"] = points
        
        # Check back navigation
        if request.back_nav_count > self.THRESHOLDS["back_nav_count"]:
            points = self.WEIGHTS["back_nav"]
            score += points
            breakdown["back_navigation"] = points
        
        # Check price checking
        if request.price_check_count > self.THRESHOLDS["price_check_count"]:
            points = self.WEIGHTS["price_check"]
            score += points
            breakdown["price_checking"] = points
        
        # Check payment failures
        if request.payment_retry_count > self.THRESHOLDS["payment_retry_count"]:
            points = self.WEIGHTS["payment_failure"]
            score += points
            breakdown["payment_failure"] = points
        
        # Check high-value event
        if request.event_type and request.event_type.upper() in self.HIGH_VALUE_EVENTS:
            points = self.WEIGHTS["high_value_event"]
            score += points
            breakdown["high_value_event"] = points
        
        # Check first-time user
        if request.is_first_time_user:
            points = self.WEIGHTS["first_time_user"]
            score += points
            breakdown["first_time_user"] = points
        
        # Cap at 100
        score = min(score, 100)
        
        # Determine if help should be shown
        should_show_help = score >= settings.FRICTION_THRESHOLD
        
        # Get appropriate help message
        help_message = self._get_help_message(request.current_screen, request.payment_retry_count)
        
        return FrictionDetectResponse(
            friction_score=score,
            should_show_help=should_show_help,
            help_message=help_message if should_show_help else None,
            breakdown=breakdown
        )
    
    def _get_help_message(self, screen: Optional[str], payment_retries: int) -> str:
        """Get contextual help message based on current screen."""
        if payment_retries > 0:
            return self.HELP_MESSAGES["payment"]
        
        if screen:
            screen_lower = screen.lower()
            if "checkout" in screen_lower or "cart" in screen_lower:
                return self.HELP_MESSAGES["checkout"]
            elif "menu" in screen_lower or "platter" in screen_lower:
                return self.HELP_MESSAGES["menu"]
            elif "custom" in screen_lower:
                return self.HELP_MESSAGES["customization"]
        
        return self.HELP_MESSAGES["default"]
    
    def get_score_interpretation(self, score: float) -> str:
        """Get human-readable interpretation of score."""
        if score >= 80:
            return "CRITICAL - User likely frustrated, immediate attention needed"
        elif score >= 60:
            return "HIGH - User showing significant friction signals"
        elif score >= 40:
            return "MODERATE - Some friction detected"
        elif score >= 20:
            return "LOW - Minor friction signals"
        else:
            return "MINIMAL - User journey appears smooth"
