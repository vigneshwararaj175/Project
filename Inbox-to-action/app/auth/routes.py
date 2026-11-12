import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from app.database import supabase
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth")
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

class Credentials(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(body: Credentials):
    try:
        resp = supabase.auth.sign_up({"email": body.email, "password": body.password})
        return {"access_token": resp.session.access_token if resp.session else None,
                "user_id": resp.user.id}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/login")
def login(body: Credentials):
    try:
        resp = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
        return {"access_token": resp.session.access_token, "user_id": resp.user.id}
    except Exception as e:
        raise HTTPException(401, str(e))

def _flow():
    client_config = {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [os.environ["GOOGLE_REDIRECT_URI"]]
        }
    }
    return Flow.from_client_config(
        client_config, 
        scopes=SCOPES, 
        redirect_uri=os.environ["GOOGLE_REDIRECT_URI"]
    )

@router.get("/gmail/start")
def gmail_start(user=Depends(get_current_user)):
    flow = _flow()
    url, _ = flow.authorization_url(
        state=user.id, access_type="offline", prompt="consent"
    )
    return {"url": url} 

@router.get("/gmail/callback")
def gmail_callback(code: str, state: str):
    flow = _flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    supabase.table("integrations").upsert({
        "user_id": state,
        "provider": "gmail",
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_expiry": creds.expiry.isoformat() if creds.expiry else None,
    }, on_conflict="user_id,provider").execute()

    # This line sends the user back to the homepage instead of showing raw JSON
    return RedirectResponse(url="/")