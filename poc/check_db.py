
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def check_conversation():
    database_url = os.getenv("DATABASE_URL")
    conversation_id = "dfcefe3c-8a67-4699-b5e7-d6d90694266e"  # Correct ID from screenshot
    
    engine = create_async_engine(database_url)
    async with engine.connect() as conn:
        print(f"🔍 Checking for Conversation ID: {conversation_id}")
        
        result = await conn.execute(text(
            f"SELECT id, user_id, conversation_id, created_at FROM incidences WHERE conversation_id = '{conversation_id}'"
        ))
        row = result.fetchone()
        
        if row:
            print(f"✅ FOUND! Linked to Incidence: {row[0]}")
            print(f"   User: {row[1]}")
            print(f"   Created: {row[3]}")
        else:
            print("❌ NOT FOUND in database.")
            
            # Check most recent 5 incidences to see what's there
            print("\nRecent Incidences:")
            recent = await conn.execute(text(
                "SELECT id, user_id, conversation_id, created_at FROM incidences ORDER BY created_at DESC LIMIT 5"
            ))
            for r in recent:
                print(f" - {r[0]} | Conv: {r[2]} | {r[3]}")

if __name__ == "__main__":
    asyncio.run(check_conversation())
