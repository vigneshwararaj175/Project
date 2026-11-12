import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.gmail.client import get_gmail_service, list_recent_messages, get_message
from app.gmail.parser import extract_plain_text
from app.agent.extractor import extract_actions
from app.database import save_action, supabase
from app.gmail.client import get_gmail_service, list_recent_messages, get_message, mark_message_as_read
router = APIRouter()

@router.post("/api/process-inbox")
def process_inbox(user=Depends(get_current_user), max_results: int = 5):
    # 1. Fetch the token from Supabase
    res = supabase.table("integrations").select("*").eq("user_id", user.id).eq("provider", "gmail").execute()
    
    # 2. If no token exists, tell them to connect
    if not res.data:
        raise HTTPException(400, "Please connect your Gmail account first by clicking 'Connect Gmail'.")
    
    token_data = res.data[0]
    
    # 3. Create the service using the token data
    try:
        svc = get_gmail_service(token_data)
    except Exception as e:
        raise HTTPException(400, f"Error loading Gmail token: {str(e)}")

    # --- The rest of the function stays exactly the same! ---
    msgs = list_recent_messages(svc, max_results=max_results)
    created = 0
    
    for m in msgs:
        full = get_message(svc, m["id"])
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        text = extract_plain_text(full["payload"])
        if not text:
            continue
        
        actions = extract_actions(text, headers.get("Subject", ""), date.today().isoformat())
        
        for a in actions:
            save_action(user.id, m["id"], {
                "subject": headers.get("Subject"),
                "sender": headers.get("From"),
                "threadId": full["threadId"],
            }, a)
            created += 1
            
        # NEW: Mark the email as read now that we've processed it
        mark_message_as_read(svc, m["id"])

@router.get("/api/actions")
def list_actions(user=Depends(get_current_user)):
    resp = supabase.table("action_items").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
    return resp.data

@router.put("/api/actions/{task_id}/complete")
def complete_task(task_id: int, user=Depends(get_current_user)):
    resp = supabase.table("action_items").update({"status": "completed"}).eq("id", task_id).eq("user_id", user.id).execute()
    if not resp.data:
        raise HTTPException(404, "Task not found or not owned by user")
    return {"status": "success", "message": "Task marked as completed"}