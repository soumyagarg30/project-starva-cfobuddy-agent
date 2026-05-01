# Manages async Neon PostgreSQL connection pooling with configurable limits.
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIG (EDIT HERE)
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", 1))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", 5))

# =========================
# GLOBAL POOL
# =========================

_pool = None


async def get_pool():
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=DB_POOL_MIN,
            max_size=DB_POOL_MAX,
        )

    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None