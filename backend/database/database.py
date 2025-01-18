from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_USE_TLS,
    MONGODB_CA_FILE
)
from schemas.user import User

client = AsyncIOMotorClient(
    MONGODB_URI,
    tls=MONGODB_USE_TLS,
    tlsCAFile=MONGODB_CA_FILE
)

DB = client[MONGODB_DB_NAME]


async def setup():
    await init_beanie(
        database=DB,
        document_models=[
            User
        ]
    )
