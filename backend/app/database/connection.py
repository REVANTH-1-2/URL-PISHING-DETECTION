import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger("phishing_system")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1000)
        # Ping server to verify active MongoDB connection
        await client.admin.command('ping')
        
        db.client = client
        db.db = db.client[settings.MONGODB_DATABASE]
        logger.info("Successfully connected to MongoDB.")
        
        # Create database indexes
        await init_db_indexes()
    except Exception as e:
        logger.warning(f"MongoDB connection unavailable ({e}). Backend running in Standalone ML Mode.")
        db.client = None
        db.db = None

async def close_mongo_connection():
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed.")

async def init_db_indexes():
    if db.db is None:
        return
    try:
        # Users index
        await db.db.users.create_index("email", unique=True)
        # Scans indexes
        await db.db.scans.create_index([("user_id", 1), ("created_at", -1)])
        await db.db.scans.create_index("prediction")
        await db.db.scans.create_index("input_type")
        # Model metrics indexes
        await db.db.model_metrics.create_index([("dataset", 1), ("model", 1), ("evaluation_type", 1)])
        logger.info("Database indexes initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")

def get_database():
    return db.db
