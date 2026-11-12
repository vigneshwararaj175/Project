from dotenv import load_dotenv
load_dotenv()

from app.database import supabase

resp = supabase.table("action_items").select("*").limit(5).execute()
print("Rows:", resp.data)
print("✅ Connected to Supabase")