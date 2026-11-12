import os
from supabase import create_client, Client

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

def save_action(user_id: str, email_id: str, meta: dict, action) -> None:
    supabase.table("action_items").insert({
        "user_id": user_id,
        "email_id": email_id,
        "subject": meta.get("subject"),
        "sender": meta.get("sender"),
        "thread_id": meta.get("threadId"),
        "action_type": action.action_type,
        "title": action.title,
        "description": action.description,
        "due_date": action.due_date.isoformat() if action.due_date else None,
        "priority": action.priority,
        "raw_email_snippet": action.source_snippet,
    }).execute()