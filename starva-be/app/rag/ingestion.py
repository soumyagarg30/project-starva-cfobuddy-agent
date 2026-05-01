import sys
import os

# Add required paths so we can import from 'app' and 'starva-be' root
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../..')))

import asyncio

from embeddings.embedding_model import embed_text
from databases.db_postgres import insert_document, init_db
from knowledge.seed_data import DATA


async def ingest():
    print("🚀 Starting ingestion...")

    await init_db()

    for text in DATA:
        embedding = embed_text(text)

        await insert_document(
            content=text,
            embedding=embedding,
            metadata={"type": "knowledge"},
            source="seed"
        )

        print("✅ Inserted:", text)

    print("🎉 Ingestion complete")


if __name__ == "__main__":
    asyncio.run(ingest())