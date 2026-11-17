# 📥 Inbox to Action

An AI-powered productivity agent that connects to your Gmail, reads your unread emails, and automatically extracts actionable tasks, priorities, and due dates into a sleek, dark-mode dashboard.

## 🚀 Live Demo
You can try the live application here: **[https://inbox-to-action.fly.dev](https://inbox-to-action.fly.dev)**

---

## ✨ Features

*   **Secure Authentication:** Users can sign up and log in securely via Supabase Auth.
*   **Google OAuth 2.0:** Users can safely connect their Gmail accounts. Tokens are securely stored in the database.
*   **AI-Powered Extraction:** Uses Groq (Llama 3) to analyze email text and extract tasks, resolving relative dates (e.g., "by Friday") into actual `YYYY-MM-DD` formats.
*   **Smart Filtering:** Only processes **unread** emails to prevent duplicate task creation.
*   **Auto-Mark as Read:** Automatically marks processed emails as read in the user's Gmail inbox.
*   **Task Management:** Users can view their tasks categorized by priority (High, Medium, Low) and mark them as completed.
*   **Cinematic UI:** A premium, responsive dark-mode interface built with Tailwind CSS, featuring ambient lighting and glassmorphism.

---

## 🛠️ Tech Stack

**Backend:**
*   [Python 3.12](https://www.python.org/)
*   [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
*   [Groq API](https://groq.com/) - Ultra-fast LLM inference (Llama 3)
*   [Supabase](https://supabase.com/) - PostgreSQL Database & Authentication
*   [Google API Python Client](https://developers.google.com/gmail/api) - Gmail integration

**Frontend:**
*   [Jinja2](https://jinja.palletsprojects.com/) - HTML templating
*   [Tailwind CSS](https://tailwindcss.com/) - Styling and animations (via CDN)
*   [Lucide Icons](https://lucide.dev/) - UI Icons
*   Vanilla JavaScript (Fetch API)

**Infrastructure:**
*   [Docker](https://www.docker.com/) - Containerization
*   [Fly.io](https://fly.io/) - Cloud hosting

---

## ⚙️ How It Works (Architecture)

1.  **Authentication:** The user signs up/logs in via the frontend. FastAPI validates the credentials with Supabase and returns a JWT.
2.  **Authorization:** The user clicks "Connect Gmail". FastAPI redirects them to Google's OAuth consent screen. Upon approval, FastAPI receives the tokens and securely stores them in the Supabase `integrations` table.
3.  **Processing:** When the user clicks "Process Inbox", FastAPI:
    *   Fetches the user's OAuth token from Supabase.
    *   Calls the Gmail API to fetch **unread** inbox messages.
    *   Parses the raw email MIME data into plain text.
    *   Sends the text to the **Groq AI API** with strict Pydantic schemas to extract structured JSON tasks.
    *   Saves the tasks to the Supabase `action_items` table.
    *   Marks the processed emails as "read" in Gmail.
4.  **Completion:** The user clicks a task card, which triggers a `PUT` request to update the task status to `completed` in Supabase.

---

## 💻 Local Development Setup

### Prerequisites
*   Python 3.12+
*   Google Cloud Console project (with Gmail API enabled)
*   Supabase account
*   Groq API key

### 1. Clone the repository
```bash
git clone https://github.com/vigneshwararaj175/Project.git
cd Project/Inbox-to-action


### 2. Set up the virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and add the following keys:

```env
GROQ_API_KEY=gsk_your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/gmail/callback
SECRET_KEY=your_random_secret_hex
```

### 5. Supabase Database Setup
Run the following SQL in your Supabase SQL Editor to create the necessary tables:
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE integrations (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  provider TEXT NOT NULL DEFAULT 'gmail',
  access_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  token_expiry TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, provider)
);

CREATE TABLE action_items (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  email_id TEXT NOT NULL,
  thread_id TEXT,
  subject TEXT,
  sender TEXT,
  action_type TEXT,
  title TEXT NOT NULL,
  description TEXT,
  due_date TIMESTAMPTZ,
  priority TEXT,
  status TEXT DEFAULT 'pending',
  raw_email_snippet TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 6. Run the Application
```bash
uvicorn app.main:app --reload
```
Open `http://localhost:8000` in your browser.

---

## ☁️ Deployment (Fly.io)

This project is configured for deployment on Fly.io.

1. Install the Fly CLI: `iwr https://fly.io/install.ps1 -useb | iex`
2. Log in: `fly auth login`
3. Launch the app (ensure `Dockerfile` and `fly.toml` are present): `fly launch --no-deploy`
4. Set your secrets on Fly.io:
   ```bash
   fly secrets set GROQ_API_KEY="your_key"
   fly secrets set SUPABASE_URL="your_url"
   fly secrets set SUPABASE_SERVICE_KEY="your_key"
   fly secrets set GOOGLE_CLIENT_ID="your_id"
   fly secrets set GOOGLE_CLIENT_SECRET="your_secret"
   fly secrets set GOOGLE_REDIRECT_URI="https://your-app-name.fly.dev/auth/gmail/callback"
   fly secrets set SECRET_KEY="your_secret"
   ```
5. Deploy: `fly deploy`

---

