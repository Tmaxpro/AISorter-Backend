from pymongo import MongoClient
from core.config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.DB_NAME]
collection = db[settings.COLLECTION_NAME]
