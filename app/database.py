import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from datetime import datetime

client = None
db = None

def connect_db(uri):
    global client, db
    if not uri:
        print("⚠️ MongoDB URI not provided")
        return
        
    try:
        print(f"Connecting to MongoDB...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        db = client["serena_bot"]
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        client = None
        db = None
