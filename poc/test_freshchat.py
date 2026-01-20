
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://craftmyplate-932159069325046075-cefb1bc4cb2de9817685613.freshchat.com/v2"
API_KEY = os.getenv("FRESHCHAT_APP_KEY")

async def test_api():
    print(f"Testing API: {API_URL}")
    print(f"Using Key: {API_KEY[:5]}..." if API_KEY else "No Key")
    
    async with httpx.AsyncClient() as client:
        # Attempt 1: Bearer Token
        print("\n--- Attempt 1: Bearer Token ---")
        headers = {"Authorization": f"Bearer {API_KEY}"}
        resp = await client.get(f"{API_URL}/channels", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

        # Attempt 2: Direct Token (No Bearer)
        print("\n--- Attempt 2: Direct Token (No Bearer) ---")
        headers = {"Authorization": API_KEY}
        resp = await client.get(f"{API_URL}/channels", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

        
if __name__ == "__main__":
    asyncio.run(test_api())
