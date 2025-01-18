from asyncio import run

from api import run_api
from database.database import setup

from schemas.user import User, UserUpdate, UserBase
from snowflake import SnowflakeID

async def main():
    await setup()

    user = User(name="123", password=b"123")
    print(SnowflakeID)
    # await User.insert(user)

    await run_api()

if __name__ == "__main__":
    run(main=main())