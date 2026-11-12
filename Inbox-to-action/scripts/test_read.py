from app.gmail.client import get_gmail_service, list_recent_messages, get_message
from app.gmail.parser import extract_plain_text

svc = get_gmail_service()
msgs = list_recent_messages(svc, 3)
print(f"Found {len(msgs)} messages\n")
for m in msgs:
    full = get_message(svc, m["id"])
    headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
    text = extract_plain_text(full["payload"])
    print("─" * 60)
    print(f"SUBJECT: {headers.get('Subject')}")
    print(f"FROM:    {headers.get('From')}")
    print(f"TEXT:    {text[:200]}...\n")