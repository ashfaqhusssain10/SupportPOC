import asyncio
import asyncpg

async def test():
    try:
        # Test with no password (trust mode) on port 5433
        conn = await asyncpg.connect(user='poc_user', database='support_system', host='localhost', port=5433)
        user = await conn.fetchval('SELECT current_user')
        print(f'SUCCESS: Connected as {user}')
        await conn.close()
    except Exception as e:
        print(f'FAILED: {e}')

asyncio.run(test())
