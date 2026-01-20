"""
Freshchat Service - Send messages via Freshchat Conversations API.
"""

import httpx
from app.config import settings


class FreshchatService:
    """Service for interacting with Freshchat API."""
    
    def __init__(self):
        self.api_url = settings.FRESHCHAT_API_URL
        self.api_key = settings.FRESHCHAT_APP_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self, 
        conversation_id: str, 
        message: str,
        actor_type: str = "agent",
        actor_id: str = None
    ) -> dict:
        """
        Send a message to a conversation.
        """
        url = f"{self.api_url}/conversations/{conversation_id}/messages"
        
        payload = {
            "message_parts": [
                {
                    "text": {
                        "content": message
                    }
                }
            ],
            "actor_type": actor_type
        }
        
        if actor_id:
            payload["actor_id"] = actor_id
            
        print(f"🚀 Sending to Freshchat: {url}")
        print(f"📦 Payload: {payload}")
        print(f"🔑 Key Prefix: {self.api_key[:5] if self.api_key else 'None'}...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                print(f"📥 Response Status: {response.status_code}")
                print(f"📄 Response Body: {response.text}")
                
                if response.status_code in [200, 201]:
                    print(f"✅ Message sent to conversation {conversation_id}")
                    return {"success": True, "data": response.json()}
                else:
                    print(f"❌ Failed to send message: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text, "status_code": response.status_code}
                    
            except httpx.RequestError as e:
                print(f"❌ HTTP Error: {e}")
                return {"success": False, "error": str(e)}
    
    async def get_conversation(self, conversation_id: str) -> dict:
        """Get conversation details."""
        url = f"{self.api_url}/conversations/{conversation_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
    
    async def get_user(self, user_id: str) -> dict:
        """Get user details from Freshchat API (including email)."""
        url = f"{self.api_url}/users/{user_id}"
        
        print(f"🔍 Fetching user details for: {user_id}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                
                print(f"📥 User API Response: {response.status_code}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ User data: {user_data}")
                    return {"success": True, "data": user_data}
                else:
                    print(f"❌ Failed to get user: {response.text}")
                    return {"success": False, "error": response.text}
            except Exception as e:
                print(f"❌ Error fetching user: {e}")
                return {"success": False, "error": str(e)}


# Singleton instance
freshchat_service = FreshchatService()
