"""
Freshdesk Ticket Service - Sync incidence data to Freshdesk tickets via custom fields.
"""
import httpx
from typing import Optional
from app.config import settings


class FreshdeskTicketService:
    """Service to interact with Freshdesk Tickets API."""
    
    def __init__(self):
        # Freshdesk uses API key + "X" as password for Basic Auth
        self.domain = settings.FRESHDESK_DOMAIN  # e.g., "craftmyplate"
        self.api_key = settings.FRESHDESK_API_KEY
        self.base_url = f"https://{self.domain}.freshdesk.com/api/v2"
        self.auth = (self.api_key, "X")  # Freshdesk uses API key as username, "X" as password
    
    async def find_ticket_by_email(self, email: str) -> Optional[dict]:
        """Find the most recent open ticket for a given email."""
        url = f"{self.base_url}/search/tickets"
        params = {
            "query": f'"requester_email:\'{email}\' AND status:2"'  # status:2 = Open
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, auth=self.auth, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        return results[0]  # Return most recent
                return None
            except Exception as e:
                print(f"❌ Error searching tickets: {e}")
                return None
    
    async def update_ticket_custom_fields(
        self,
        ticket_id: int,
        friction_score: float = 0,
        cart_value: float = 0,
        stage: str = "unknown",
        guest_count: int = 0,
        conversation_id: str = None
    ) -> bool:
        """
        Update a Freshdesk ticket with custom field data from our incidence.
        
        NOTE: You must first create these custom fields in Freshdesk Admin:
        - cf_friction_score (Number)
        - cf_cart_value (Number)
        - cf_order_stage (Dropdown or Text)
        - cf_guest_count (Number)
        - cf_freshchat_conversation_id (Text)
        """
        url = f"{self.base_url}/tickets/{ticket_id}"
        
        payload = {
            "custom_fields": {
                "cf_friction_score": int(friction_score),
                "cf_cart_value": int(cart_value),
                "cf_order_stage": stage,
                "cf_guest_count": int(guest_count),
                "cf_freshchat_conversation_id": conversation_id
            }
        }
        
        print(f"📤 Updating Freshdesk Ticket #{ticket_id} with: {payload}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    url,
                    json=payload,
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    print(f"✅ Ticket #{ticket_id} updated successfully!")
                    return True
                else:
                    print(f"❌ Failed to update ticket: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error updating ticket: {e}")
                return False
    
    async def create_ticket(
        self,
        email: str,
        subject: str,
        description: str,
        friction_score: float = 0,
        cart_value: float = 0,
        stage: str = "unknown",
        guest_count: int = 0,
        conversation_id: str = None,
        source: int = 1  # Default to 1 (Email). Use 7 for Chat.
    ) -> Optional[dict]:
        """
        Create a new Freshdesk ticket with custom fields pre-populated.
        """
        url = f"{self.base_url}/tickets"
        
        payload = {
            "email": email,
            "subject": subject,
            "description": description,
            "status": 2,  # Open
            "priority": 2 if friction_score < 5 else 3,  # High priority if friction > 5
            "source": source,
            "custom_fields": {
                "cf_friction_score": int(friction_score),
                "cf_cart_value": int(cart_value),
                "cf_order_stage": stage,
                "cf_guest_count": int(guest_count),
                "cf_freshchat_conversation_id": conversation_id
            }
        }
        
        print(f"📤 Creating Freshdesk Ticket for {email}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    ticket = response.json()
                    print(f"✅ Ticket created: #{ticket.get('id')}")
                    return ticket
                else:
                    print(f"❌ Failed to create ticket: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error creating ticket: {e}")
                return None


# Singleton instance
freshdesk_ticket_service = FreshdeskTicketService()
