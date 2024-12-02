import asyncio
import asyncpg
import time
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "qweasdzxc",
    "database": "test_db"
}

MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB = "test_db"


ITERATIONS = 1000


class MongoRecord(Document):
    name: str


async def init_postgres():
    conn = await asyncpg.connect(**POSTGRES_CONFIG)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
    """)
    print(f"PostgreSQL: Created table test_table")

    await conn.close()


async def insert_into_postgresql(name: str):
    conn = await asyncpg.connect(**POSTGRES_CONFIG)
    await conn.execute("INSERT INTO test_table(name) VALUES($1)", name)
    await conn.close()


async def insert_into_mongodb(name: str):
    record = MongoRecord(name=name)
    await record.insert()


async def postgresql_insertions():
    print("Starting PostgreSQL insertions...")
    start_time = time.time()

    for i in range(ITERATIONS):
        await insert_into_postgresql(f"record_{i}")

    end_time = time.time()
    print(f"PostgreSQL: Inserted {ITERATIONS} records in {end_time - start_time} seconds")


async def mongodb_insertions():
    print("Starting MongoDB insertions...")
    start_time = time.time()

    for i in range(ITERATIONS):
        await insert_into_mongodb(f"record_{i}")

    end_time = time.time()
    print(f"MongoDB: Inserted {ITERATIONS} records in {end_time - start_time} seconds")


async def main():
    await init_postgres()

    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client[MONGODB_DB], document_models=[MongoRecord])

    await mongodb_insertions()
    await postgresql_insertions()


if __name__ == "__main__":
    asyncio.run(main())
