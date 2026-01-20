"""
Freshworks Omnichannel Integration Verification Script

This comprehensive script verifies all integration points between:
- Freshchat (Chat Widget)
- Freshdesk (Ticket System)

Based on research from Freshworks API documentation:
- GET /v2/accounts/configuration - Account info including bundle_id, datacenter
- GET /v2/channels - List all chat channels
- GET /v2/users - User management
- GET /v2/conversations - Conversation management
- Freshdesk API for ticket verification

Run this script to ensure your Omnichannel integration is properly configured.
"""

import asyncio
import httpx
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OmnichannelVerifier:
    """Comprehensive Freshworks Omnichannel Integration Verifier."""
    
    def __init__(self):
        # Freshchat credentials
        self.freshchat_api_key = os.getenv("FRESHCHAT_APP_KEY")
        self.freshchat_app_id = os.getenv("FRESHCHAT_APP_ID")
        
        # Freshdesk credentials
        self.freshdesk_api_key = os.getenv("FRESHDESK_API_KEY")
        self.freshdesk_domain = os.getenv("FRESHDESK_DOMAIN", "test2288")
        
        # API URLs (will be updated based on datacenter)
        self.freshchat_api_url = "https://api.in.freshchat.com/v2"  # Default to India
        self.freshdesk_api_url = f"https://{self.freshdesk_domain}.freshdesk.com/api/v2"
        
        # Results storage
        self.results = []
        self.account_config = {}
        
    def log(self, status: str, category: str, message: str, details: dict = None):
        """Log a verification result."""
        emoji = {
            "pass": "✅",
            "fail": "❌", 
            "warn": "⚠️",
            "info": "ℹ️",
            "skip": "⏭️"
        }.get(status, "•")
        
        print(f"{emoji} [{category}] {message}")
        if details:
            for key, value in details.items():
                print(f"   └─ {key}: {value}")
        
        self.results.append({
            "status": status,
            "category": category,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    # ========== CREDENTIAL VERIFICATION ==========
    
    async def verify_credentials(self):
        """Verify all required credentials are present."""
        print("\n" + "="*60)
        print("🔐 CREDENTIAL VERIFICATION")
        print("="*60)
        
        all_present = True
        
        # Freshchat App ID
        if self.freshchat_app_id and self.freshchat_app_id != "your_app_id":
            self.log("pass", "Credentials", "Freshchat App ID configured", 
                    {"value": f"{self.freshchat_app_id[:8]}..."})
        else:
            self.log("fail", "Credentials", "Freshchat App ID missing or placeholder")
            all_present = False
        
        # Freshchat API Key
        if self.freshchat_api_key and len(self.freshchat_api_key) > 50:
            self.log("pass", "Credentials", "Freshchat API Key configured",
                    {"value": f"{self.freshchat_api_key[:15]}..."})
        else:
            self.log("fail", "Credentials", "Freshchat API Key missing or invalid")
            all_present = False
        
        # Freshdesk API Key
        if self.freshdesk_api_key and len(self.freshdesk_api_key) > 10:
            self.log("pass", "Credentials", "Freshdesk API Key configured",
                    {"value": f"{self.freshdesk_api_key[:10]}..."})
        else:
            self.log("fail", "Credentials", "Freshdesk API Key missing")
            all_present = False
        
        # Freshdesk Domain
        if self.freshdesk_domain:
            self.log("pass", "Credentials", "Freshdesk Domain configured",
                    {"value": f"{self.freshdesk_domain}.freshdesk.com"})
        else:
            self.log("fail", "Credentials", "Freshdesk Domain missing")
            all_present = False
        
        return all_present
    
    # ========== FRESHCHAT ACCOUNT CONFIGURATION ==========
    
    async def get_freshchat_account_config(self):
        """Get Freshchat account configuration including bundle and datacenter info."""
        print("\n" + "="*60)
        print("📊 FRESHCHAT ACCOUNT CONFIGURATION")
        print("="*60)
        
        headers = {
            "Authorization": f"Bearer {self.freshchat_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshchat_api_url}/accounts/configuration",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    config = response.json()
                    self.account_config = config
                    
                    self.log("pass", "Account", "Freshchat account configuration retrieved")
                    
                    # Log important configuration details
                    details = {
                        "app_id": config.get("app_id", "N/A"),
                        "account_domain": config.get("account_domain", "N/A"),
                        "datacenter": config.get("datacenter", "N/A"),
                        "bundle_type": config.get("bundle_type", "N/A"),
                        "plan_type": config.get("plan_type", "N/A")
                    }
                    
                    for key, value in details.items():
                        self.log("info", "Config", f"{key}: {value}")
                    
                    # Check if using bundle (Omnichannel)
                    bundle_id = config.get("bundle_id", 0)
                    if bundle_id and bundle_id != 0:
                        self.log("pass", "Bundle", f"Account is part of Freshworks bundle (ID: {bundle_id})",
                                {"bundle_type": config.get("bundle_type", "N/A")})
                    else:
                        self.log("warn", "Bundle", "Account is standalone Freshchat (not bundled)",
                                {"note": "Omnichannel features may be limited"})
                    
                    return True
                else:
                    self.log("fail", "Account", f"Failed to get account config (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "Account", f"Error getting account config: {str(e)}")
            return False
    
    # ========== FRESHCHAT CHANNELS ==========
    
    async def verify_freshchat_channels(self):
        """Verify Freshchat channels are configured."""
        print("\n" + "="*60)
        print("📢 FRESHCHAT CHANNELS")
        print("="*60)
        
        headers = {
            "Authorization": f"Bearer {self.freshchat_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshchat_api_url}/channels",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    channels = data.get("channels", data) if isinstance(data, dict) else data
                    
                    if isinstance(channels, list) and len(channels) > 0:
                        self.log("pass", "Channels", f"Found {len(channels)} channel(s)")
                        for channel in channels[:5]:  # Show max 5
                            name = channel.get("name", "Unnamed")
                            channel_id = channel.get("id", "N/A")
                            enabled = channel.get("enabled", True)
                            status = "✓" if enabled else "✗"
                            print(f"   └─ {status} {name} (ID: {channel_id[:8]}...)")
                        return True
                    else:
                        self.log("warn", "Channels", "No channels found or empty response")
                        return True
                else:
                    self.log("fail", "Channels", f"Failed to get channels (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "Channels", f"Error getting channels: {str(e)}")
            return False
    
    # ========== FRESHCHAT AGENTS ==========
    
    async def verify_freshchat_agents(self):
        """Verify Freshchat agents are configured."""
        print("\n" + "="*60)
        print("👥 FRESHCHAT AGENTS")
        print("="*60)
        
        headers = {
            "Authorization": f"Bearer {self.freshchat_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshchat_api_url}/agents",
                    headers=headers,
                    params={"items_per_page": 10},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get("agents", data) if isinstance(data, dict) else data
                    
                    if isinstance(agents, list) and len(agents) > 0:
                        self.log("pass", "Agents", f"Found {len(agents)} agent(s)")
                        for agent in agents[:5]:
                            email = agent.get("email", "N/A")
                            role = agent.get("role_name", agent.get("role", "N/A"))
                            status = agent.get("availability_status", "N/A")
                            print(f"   └─ {email} ({role}) - {status}")
                        return True
                    else:
                        self.log("warn", "Agents", "No agents found")
                        return True
                else:
                    self.log("fail", "Agents", f"Failed to get agents (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "Agents", f"Error getting agents: {str(e)}")
            return False
    
    # ========== FRESHDESK API VERIFICATION ==========
    
    async def verify_freshdesk_api(self):
        """Verify Freshdesk API is accessible."""
        print("\n" + "="*60)
        print("🎫 FRESHDESK API")
        print("="*60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshdesk_api_url}/tickets",
                    auth=(self.freshdesk_api_key, "X"),
                    params={"per_page": 1},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    self.log("pass", "Freshdesk", "API connection successful")
                    return True
                elif response.status_code == 401:
                    self.log("fail", "Freshdesk", "API authentication failed (401)")
                    return False
                else:
                    self.log("fail", "Freshdesk", f"Unexpected status: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log("fail", "Freshdesk", f"Connection error: {str(e)}")
            return False
    
    # ========== FRESHDESK CUSTOM FIELDS ==========
    
    async def verify_freshdesk_custom_fields(self):
        """Verify Freshdesk has required custom fields for integration."""
        print("\n" + "="*60)
        print("📋 FRESHDESK CUSTOM FIELDS")
        print("="*60)
        
        required_fields = [
            "cf_friction_score",
            "cf_cart_value", 
            "cf_stage",
            "cf_guest_count",
            "cf_freshchat_conversation_id"
        ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshdesk_api_url}/ticket_fields",
                    auth=(self.freshdesk_api_key, "X"),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    fields = response.json()
                    field_names = [f.get("name", "") for f in fields]
                    
                    found = []
                    missing = []
                    
                    for req_field in required_fields:
                        if req_field in field_names:
                            found.append(req_field)
                        else:
                            missing.append(req_field)
                    
                    if found:
                        self.log("pass", "CustomFields", f"Found {len(found)}/{len(required_fields)} required fields")
                        for f in found:
                            print(f"   └─ ✓ {f}")
                    
                    if missing:
                        self.log("warn", "CustomFields", f"Missing {len(missing)} fields (may need to create)")
                        for f in missing:
                            print(f"   └─ ✗ {f}")
                    
                    return len(missing) == 0
                else:
                    self.log("fail", "CustomFields", f"Could not fetch fields (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "CustomFields", f"Error checking fields: {str(e)}")
            return False
    
    # ========== END-TO-END FLOW TEST ==========
    
    async def test_user_lookup(self, user_id: str = None):
        """Test if a specific user can be looked up."""
        if not user_id:
            print("\n⏭️  Skipping user lookup test (no user_id provided)")
            return True
        
        print("\n" + "="*60)
        print("👤 USER LOOKUP TEST")
        print("="*60)
        
        headers = {
            "Authorization": f"Bearer {self.freshchat_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshchat_api_url}/users/{user_id}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    user = response.json()
                    email = user.get("email", "N/A")
                    name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    self.log("pass", "UserLookup", f"User found: {name}",
                            {"email": email, "id": user_id[:16] + "..."})
                    return True
                else:
                    self.log("fail", "UserLookup", f"User not found (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "UserLookup", f"Error: {str(e)}")
            return False
    
    async def test_conversation_access(self, conversation_id: str = None):
        """Test if a conversation can be accessed."""
        if not conversation_id:
            print("\n⏭️  Skipping conversation test (no conversation_id provided)")
            return True
        
        print("\n" + "="*60)
        print("💬 CONVERSATION ACCESS TEST")
        print("="*60)
        
        headers = {
            "Authorization": f"Bearer {self.freshchat_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshchat_api_url}/conversations/{conversation_id}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    conv = response.json()
                    status = conv.get("status", "N/A")
                    self.log("pass", "Conversation", "Conversation accessible",
                            {"status": status, "id": conversation_id[:16] + "..."})
                    return True
                else:
                    self.log("fail", "Conversation", f"Not accessible (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "Conversation", f"Error: {str(e)}")
            return False
    
    async def check_recent_tickets(self, email: str = "syed.ashfaque@craftmyplate.com"):
        """Check for recent tickets to verify ticket creation works."""
        print("\n" + "="*60)
        print("🎫 RECENT TICKETS CHECK")
        print("="*60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.freshdesk_api_url}/tickets",
                    auth=(self.freshdesk_api_key, "X"),
                    params={"email": email, "per_page": 5},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    tickets = response.json()
                    if tickets:
                        self.log("pass", "Tickets", f"Found {len(tickets)} ticket(s) for {email}")
                        for t in tickets[:3]:
                            print(f"   └─ #{t['id']}: {t.get('subject', 'N/A')[:40]}")
                    else:
                        self.log("info", "Tickets", f"No tickets found for {email}")
                    return True
                else:
                    self.log("fail", "Tickets", f"Could not fetch tickets (Status: {response.status_code})")
                    return False
                    
        except Exception as e:
            self.log("fail", "Tickets", f"Error: {str(e)}")
            return False
    
    # ========== SUMMARY ==========
    
    def print_summary(self):
        """Print comprehensive verification summary."""
        print("\n" + "="*60)
        print("📊 VERIFICATION SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        warnings = sum(1 for r in self.results if r["status"] == "warn")
        info = sum(1 for r in self.results if r["status"] == "info")
        
        print(f"\n✅ Passed:   {passed}")
        print(f"❌ Failed:   {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"ℹ️  Info:     {info}")
        
        # Integration status
        print("\n" + "-"*40)
        print("INTEGRATION STATUS:")
        print("-"*40)
        
        if failed == 0:
            print("🎉 All critical checks passed!")
            print("✓ Freshchat API: Connected")
            print("✓ Freshdesk API: Connected")
            print("✓ User Management: Working")
            print("✓ Conversation Access: Working")
            
            if self.account_config.get("bundle_id", 0) != 0:
                print("✓ Freshworks Bundle: Enabled (Omnichannel)")
            else:
                print("⚠ Freshworks Bundle: Standalone mode")
        else:
            print("🔧 Some checks failed. Review the issues above.")
            if failed > 0:
                print("\nFailed checks:")
                for r in self.results:
                    if r["status"] == "fail":
                        print(f"   ✗ {r['category']}: {r['message']}")
        
        print("\n" + "="*60)
        
        # Save report
        self.save_report()
    
    def save_report(self):
        """Save verification report to file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "account_config": self.account_config,
            "results": self.results,
            "summary": {
                "passed": sum(1 for r in self.results if r["status"] == "pass"),
                "failed": sum(1 for r in self.results if r["status"] == "fail"),
                "warnings": sum(1 for r in self.results if r["status"] == "warn")
            }
        }
        
        with open("integration_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: integration_report.json")
    
    # ========== MAIN RUNNER ==========
    
    async def run_all_checks(self, user_id: str = None, conversation_id: str = None, email: str = None):
        """Run all verification checks."""
        print("="*60)
        print("🔍 FRESHWORKS OMNICHANNEL INTEGRATION VERIFIER")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Credential verification
        creds_ok = await self.verify_credentials()
        if not creds_ok:
            print("\n⛔ Cannot continue: Missing required credentials")
            return
        
        # 2. Freshchat Account Configuration
        await self.get_freshchat_account_config()
        
        # 3. Freshchat Channels
        await self.verify_freshchat_channels()
        
        # 4. Freshchat Agents
        await self.verify_freshchat_agents()
        
        # 5. Freshdesk API
        await self.verify_freshdesk_api()
        
        # 6. Freshdesk Custom Fields
        await self.verify_freshdesk_custom_fields()
        
        # 7. User Lookup Test
        if user_id:
            await self.test_user_lookup(user_id)
        
        # 8. Conversation Access Test
        if conversation_id:
            await self.test_conversation_access(conversation_id)
        
        # 9. Recent Tickets Check
        if email:
            await self.check_recent_tickets(email)
        
        # Summary
        self.print_summary()


async def main():
    verifier = OmnichannelVerifier()
    
    # Known IDs from your session (update these as needed)
    await verifier.run_all_checks(
        user_id="a5f651e9-eeb4-4d0f-d36d-11909772c418",
        conversation_id="c2231702-1cf1-4614-aa7e-3f7fe9fd1c86",
        email="syed.ashfaque@craftmyplate.com"
    )


if __name__ == "__main__":
    asyncio.run(main())
