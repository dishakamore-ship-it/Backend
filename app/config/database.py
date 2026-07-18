from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URL)

db = client[DATABASE_NAME]


class Database:

    @staticmethod
    async def connect_db():
        try:
            await client.admin.command("ping")
            print("MongoDB Atlas Connected ✅")
        except Exception as e:
            print("MongoDB Error:", e)


    @staticmethod
    async def close_db():
        client.close()
        print("MongoDB Disconnected")


    @staticmethod
    def get_db():
        return db