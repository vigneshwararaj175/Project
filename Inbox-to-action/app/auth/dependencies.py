from fastapi import Header, HTTPException
from app.database import supabase

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.removeprefix("Bearer ")
    try:
        resp = supabase.auth.get_user(token)
        return resp.user
    except Exception:
        raise HTTPException(401, "Invalid token")