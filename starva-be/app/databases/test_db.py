import asyncio
from db_postgres import get_pool


print("🚀 Script started")

async def test_db():
    try:
        pool = await get_pool()

        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT 1;")

        print("✅ DB Connected:", result)

    except Exception as e:
        print("❌ DB Connection Failed:", str(e))


if __name__ == "__main__":
    asyncio.run(test_db())