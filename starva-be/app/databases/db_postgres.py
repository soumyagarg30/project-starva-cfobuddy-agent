# Handles pgvector schema setup, table management, and similarity search operations for CFOBuddy.

import os
import asyncio
import json
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIG (EDIT HERE)
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", 1))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", 5))

TABLE_NAME = "CFOBuddy"

# Embedding dimensionality for the pgvector column.
# Can be overridden via the EMBEDDING_DIM environment variable to match
# the active model's output size (e.g. 384, 768, 1024, ...).
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 384))

# =========================
# GLOBAL POOL (SAFE)
# =========================

_pool = None
_lock = asyncio.Lock()


async def get_pool():
    global _pool

    if _pool is None:
        async with _lock:
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


def _to_pgvector(embedding):
    """Convert a Python sequence of floats to a pgvector literal string.

    Example: [0.1, 0.2] -> "[0.1,0.2]"
    """

    # Ensure we have a plain list of floats (or values convertible to str)
    return "[" + ",".join(str(x) for x in embedding) + "]"


# =========================
# SQL DEFINITIONS
# =========================

CREATE_EXTENSION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
"""

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS "{TABLE_NAME}" (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source TEXT,
    metadata JSONB,
    agent_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR({EMBEDDING_DIM})
);
"""

CREATE_INDEX_SQL = f"""
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_embedding
ON "{TABLE_NAME}"
USING ivfflat (embedding vector_cosine_ops);
"""

# =========================
# TABLE MIGRATION HELPERS
# =========================

CHECK_EMBEDDING_COLUMN_SQL = f"""
SELECT 1
FROM information_schema.columns
WHERE table_name = '{TABLE_NAME}'
    AND column_name = 'embedding';
"""

ADD_EMBEDDING_COLUMN_SQL = f"""
ALTER TABLE "{TABLE_NAME}"
ADD COLUMN embedding VECTOR({EMBEDDING_DIM});
"""

CHECK_AGENT_TYPE_COLUMN_SQL = f"""
SELECT 1
FROM information_schema.columns
WHERE table_name = '{TABLE_NAME}'
    AND column_name = 'agent_type';
"""

ADD_AGENT_TYPE_COLUMN_SQL = f"""
ALTER TABLE "{TABLE_NAME}"
ADD COLUMN agent_type TEXT;
"""

# =========================
# INIT DB (SAFE TO RUN MANY TIMES)
# =========================


async def init_db():
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(CREATE_EXTENSION_SQL)
        await conn.execute(CREATE_TABLE_SQL)
        # Backfill "embedding" column if the table pre-existed without it.
        exists = await conn.fetchrow(CHECK_EMBEDDING_COLUMN_SQL)
        if not exists:
            await conn.execute(ADD_EMBEDDING_COLUMN_SQL)
        # Backfill "agent_type" column if the table pre-existed without it.
        agent_type_exists = await conn.fetchrow(CHECK_AGENT_TYPE_COLUMN_SQL)
        if not agent_type_exists:
            await conn.execute(ADD_AGENT_TYPE_COLUMN_SQL)
        await conn.execute(CREATE_INDEX_SQL)

    print("✅ Database initialized")


# =========================
# INSERT DOCUMENT
# =========================


async def insert_document(
    content, embedding, metadata=None, source=None, agent_type=None
):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO "{TABLE_NAME}" (content, embedding, metadata, source, agent_type)
            VALUES ($1, $2::vector, $3::jsonb, $4, $5)
            """,
            content,
            _to_pgvector(embedding),
            json.dumps(metadata) if metadata is not None else None,
            source,
            agent_type,
        )


# =========================
# SIMILARITY SEARCH
# =========================


async def similarity_search(query_embedding, limit=5):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT content, metadata, source,
                   embedding <-> $1::vector AS distance
            FROM "{TABLE_NAME}"
            ORDER BY embedding <-> $1::vector
            LIMIT {limit}
            """,
            _to_pgvector(query_embedding),
        )

    return rows


if __name__ == "__main__":
    # Simple CLI to initialize the database/table when run directly.
    print(f"Initializing table '{TABLE_NAME}' with embedding dim {EMBEDDING_DIM}...")
    if not DATABASE_URL:
        raise SystemExit(
            "DATABASE_URL is not set. Please configure it in your environment or .env file."
        )

    asyncio.run(init_db())
    print("Done.")

