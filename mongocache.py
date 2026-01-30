# ---------------------------------------------------------------
# 🔸 Shashank YT-API Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2025 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# ---------------------------------------------------------------

from pymongo import MongoClient, ASCENDING, errors
from typing import Optional, Dict, List
from datetime import datetime

MONGO_URL = "mongodb+srv://INNOMUSIC:STRANGER@innomusic.3sbcx.mongodb.net/?retryWrites=true&w=majority&appName=INNOMUSIC"
MONGO_DB = "yt_cache"
MONGO_COLL = "files"

try:
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db[MONGO_COLL]

    collection.create_index(
        [("video_id", ASCENDING), ("ext", ASCENDING)],
        unique=True
    )
    print("[MongoDB] Connected successfully and index ensured.")
except errors.ConnectionFailure as e:
    print(f"[MongoDB] Connection failed: {e}")
    collection = None


def get_cached_file(video_id: str, ext: str) -> Optional[Dict]:
    """Fetch one cached record by video_id + ext."""
    if collection is None:
        print("[MongoDB] Collection not initialized.")
        return None
    return collection.find_one({"video_id": video_id, "ext": ext})


def save_cached_file(video_id: str, ext: str, message_id: int, file_id: str) -> None:
    """Save or update cached Telegram message & file_id info."""
    if collection is None:
        print("[MongoDB] Collection not initialized.")
        return
    try:
        collection.update_one(
            {"video_id": video_id, "ext": ext},
            {
                "$set": {
                    "video_id": video_id,
                    "ext": ext,
                    "message_id": message_id,
                    "file_id": file_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            upsert=True
        )
        print(f"[MongoDB] Saved cache for {video_id}.{ext} (msg_id={message_id})")
    except errors.PyMongoError as e:
        print(f"[MongoDB] Error saving cache: {e}")


def get_all_files() -> List[Dict]:
    """Return all cached records — used for repair/recovery."""
    if collection is None:
        print("[MongoDB] Collection not initialized.")
        return []
    try:
        return list(collection.find({}, {"_id": 0}))
    except errors.PyMongoError as e:
        print(f"[MongoDB] Error fetching all files: {e}")
        return []


def delete_cached_file(video_id: str, ext: str) -> bool:
    """Delete a specific cache entry (for overwrite or corruption)."""
    if collection is None:
        print("[MongoDB] Collection not initialized.")
        return False
    try:
        result = collection.delete_one({"video_id": video_id, "ext": ext})
        if result.deleted_count:
            print(f"[MongoDB] Deleted cache for {video_id}.{ext}")
            return True
        return False
    except errors.PyMongoError as e:
        print(f"[MongoDB] Error deleting cache: {e}")
        return False
