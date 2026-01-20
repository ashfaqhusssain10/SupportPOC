"""
Verify Native Omnichannel Sync Status

This script analyzes recent Freshdesk tickets to determine if they are created 
via the Native Integration (Source: Chat) or Custom Webhook (Source: API/Email).

It also checks if the Freshchat Conversation is properly linked.
"""

import asyncio
import httpx
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class NativeSyncVerifier:
    def __init__(self):
        self.freshdesk_api_key = os.getenv("FRESHDESK_API_KEY")
        self.freshdesk_domain = os.getenv("FRESHDESK_DOMAIN", "test2288")
        self.freshchat_app_id = os.getenv("FRESHCHAT_APP_ID")
        self.freshdesk_api_url = f"https://{self.freshdesk_domain}.freshdesk.com/api/v2"
        self.email = "syed.ashfaque@craftmyplate.com"

    async def check_ticket_sources(self):
        print(f"\n🔍 Analyzing Recent Tickets for {self.email}...")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            try:
                # Fetch recent tickets
                response = await client.get(
                    f"{self.freshdesk_api_url}/tickets",
                    auth=(self.freshdesk_api_key, "X"),
                    params={
                        "email": self.email,
                        "order_by": "created_at",
                        "order_type": "desc",
                        "per_page": 5,
                        "include": "description"
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to fetch tickets: {response.text}")
                    return

                tickets = response.json()
                if not tickets:
                    print("⚠️ No tickets found.")
                    return

                print(f"Found {len(tickets)} recent tickets. Analyzing Source & Linkage:\n")
                
                native_found = False
                
                for t in tickets:
                    t_id = t['id']
                    subject = t['subject']
                    source = t.get('source', 'Unknown')
                    
                    # Source Mappings:
                    # 1: Email, 2: Portal, 3: Phone, 7: Chat, 9: Feedback Widget, 10: Outbound Email
                    source_name = {
                        1: "📧 Email (or API Default)",
                        2: "🌐 Portal",
                        7: "💬 Chat (Native Freshchat)",
                        9: "Feedback Widget",
                        10: "Outbound Email"
                    }.get(source, f"Unknown ({source})")
                    
                    created_at = t['created_at']
                    
                    print(f"🎫 Ticket #{t_id}: {subject[:40]}...")
                    print(f"   📅 Created: {created_at}")
                    print(f"   🚩 Source: {source_name}")
                    
                    # Check for Freshchat Linkage (custom fields or tags)
                    # Native integration often adds specific tags or fields
                    cf = t.get('custom_fields', {})
                    fc_conv_id = cf.get('cf_freshchat_conversation_id')
                    
                    if fc_conv_id:
                        print(f"   🔗 Custom Field Link: {fc_conv_id}")
                    else:
                        print(f"   ⚠️ No Custom Field Link")
                        
                    # Check description for "Auto-created from Freshchat" which comes from OUR webhook
                    if "Auto-created from Freshchat conversation" in t.get('description_text', ''):
                        print(f"   🤖 Origin: CUSTOM WEBHOOK (Not Native)")
                    else:
                        print(f"   👤 Origin: Likely Native or Direct")

                    if source == 7:
                        print("   ✅ SUCCESS: This is a Native Chat Ticket!")
                        native_found = True
                    else:
                        print("   ❌ ISSUE: This is NOT a Chat source ticket.")
                    
                    print("-" * 40)

                print("\n" + "="*60)
                if native_found:
                    print("✅ CONCLUSION: Native Integration is WORKING for some tickets.")
                    print("   Refer to Ticket IDs with 'Source: Chat' above.")
                else:
                    print("❌ CONCLUSION: No Native Chat tickets found.")
                    print("   All recent tickets are from Email/API/Portal sources.")
                    print("   This confirms Native Integration is NOT creating tickets.")
                    print("   Action: Check 'Marketplace & Integrations' > 'Freshdesk' settings in Freshchat.")

            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    verifier = NativeSyncVerifier()
    await verifier.check_ticket_sources()

if __name__ == "__main__":
    asyncio.run(main())
