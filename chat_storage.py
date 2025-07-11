from pymongo import MongoClient
import streamlit as st
from datetime import datetime

client = MongoClient(st.secrets["MONGO_URI"])
db = client["chat_history"]
col = db["chat_sessions"]

def save_messages(chat_id, messages, created_at=None):
    # Use first user message as title
    title = ""
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:50]
            break

    existing = col.find_one({"chat_id": chat_id})
    if not created_at:
        created_at = existing.get("created_at") if existing else datetime.now().isoformat()

    col.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_id": chat_id,
                "title": title or "Untitled",
                "messages": messages,
                "created_at": created_at,
            }
        },
        upsert=True
    )

def get_messages(chat_id):
    doc = col.find_one({"chat_id": chat_id})
    return doc["messages"] if doc else []

def get_all_chats():
    return list(col.find({}, {"chat_id": 1, "title": 1, "created_at": 1}).sort("created_at", -1))

def delete_chat(chat_id):
    col.delete_one({"chat_id": chat_id})
