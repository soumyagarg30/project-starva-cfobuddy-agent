import sys
import os
from pathlib import Path


import asyncio


# Ensure project root (starva-be) is on sys.path so `app` is importable
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from app.embeddings.embedding_model import embed_text
from app.databases.db_postgres import similarity_search, init_db


async def test():
    # Ensure DB schema (including embedding column/index) is ready
    await init_db()

    query = "Why are margins decreasing?"

    print("🔍 Query:", query)

    query_embedding = embed_text(query)

    results = await similarity_search(query_embedding)

    print("\n📊 Results:\n")

    for r in results:
        print(f"→ {r['content']}")
        print(f"   distance: {r['distance']}\n")


if __name__ == "__main__":
    asyncio.run(test())
