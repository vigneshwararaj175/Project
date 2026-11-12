import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_gmail_service(token_data: dict):
    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/gmail.readonly"] # We need to update this scope later!
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def list_recent_messages(service, max_results=10):
    # Added q="is:unread" to only fetch unread emails
    resp = service.users().messages().list(
        userId="me", 
        q="is:unread",
        labelIds=["INBOX"], 
        maxResults=max_results
    ).execute()
    return resp.get("messages", [])

def get_message(service, msg_id):
    return service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

# NEW FUNCTION: Marks an email as read
def mark_message_as_read(service, msg_id):
    try:
        service.users().messages().modify(
            userId="me", 
            id=msg_id, 
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
    except Exception as e:
        print(f"Failed to mark message {msg_id} as read: {e}")