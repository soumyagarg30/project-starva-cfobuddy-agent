# Initializes database schema (pgvector, tables, indexes) for CFOBuddy system.
import asyncio
from db_postgres import init_db

asyncio.run(init_db())