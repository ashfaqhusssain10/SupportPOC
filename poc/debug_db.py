
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def get_latest_conversation():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_async_engine(database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT id, user_id, conversation_id, created_at, channel FROM incidences ORDER BY created_at DESC LIMIT 1"
        ))
        row = result.fetchone()
        if row:
            print(f"Latest Incidence: {row}")
            if row[2]:
                print(f"Conversation ID: {row[2]}")
            else:
                print("No Conversation ID linked")
        else:
            print("No incidences found")

if __name__ == "__main__":
    asyncio.run(get_latest_conversation())
