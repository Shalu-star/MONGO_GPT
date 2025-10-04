import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri)

def get_collection(db_name, collection_name):
    client = get_mongo_client()
    db = client[db_name]
    return db[collection_name]