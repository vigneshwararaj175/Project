import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def main():
    # Find the exact folder this script is in, then go up one level to the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    creds_path = os.path.join(base_dir, "credentials.json")
    token_path = os.path.join(base_dir, "token.json")

    if not os.path.exists(creds_path):
        print(f"❌ ERROR: Still cannot find credentials.json at {creds_path}")
        return

    print(f"✅ Found credentials.json!")
    
    # Use the absolute path here
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=8080)
    
    # Save the token to the root folder
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    print(f"\n✅ Token saved to token.json")

if __name__ == "__main__":
    main()