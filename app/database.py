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
