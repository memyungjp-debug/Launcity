import os
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from realm import ScopedDatabase

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = ScopedDatabase(client[os.environ['DB_NAME']])
def now():
    return datetime.now(timezone.utc)