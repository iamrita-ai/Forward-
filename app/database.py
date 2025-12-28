import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from datetime import datetime

client = None
db = None

def connect_db(uri):
    global client, db
    client = MongoClient(uri)
    db = client["serena_bot"]

async def add_task(user_id, task_id):
    db.tasks.insert_one({
        "task_id": task_id,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    })

async def cancel_task(task_id):
    db.tasks.delete_one({"task_id": task_id})

async def get_stats():
    total_users = db.users.count_documents({})
    return {"total_users": total_users}

async def get_all_users():
    return list(db.users.find({}, {"_id": 0}))

async def set_output_channel(channel_id):
    db.settings.update_one(
        {"setting": "output_channel"},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )

async def get_output_channel():
    result = db.settings.find_one({"setting": "output_channel"})
    return result["channel_id"] if result else None

async def reset_output_channel():
    db.settings.delete_one({"setting": "output_channel"})

async def get_bot_status():
    result = db.settings.find_one({"setting": "bot_status"})
    return result["status"] if result else "on"

async def set_bot_status(status):
    db.settings.update_one(
        {"setting": "bot_status"},
        {"$set": {"status": status}},
        upsert=True
    )
