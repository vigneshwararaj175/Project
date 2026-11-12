import os
import instructor
from groq import Groq
from app.models.action import ActionItem

client = instructor.from_groq(Groq(api_key=os.environ["GROQ_API_KEY"]), mode=instructor.Mode.TOOLS)

SYSTEM = """You extract action items from emails.
Rules:
- Only extract things the recipient needs to DO.
- Ignore newsletters, marketing, and FYI-only emails (return []).
- Ignore automated system emails asking to "Confirm email", "Set password", "Reset password", or "Verify account".
- due_date must be YYYY-MM-DD; resolve relative dates using today's date.
- Priority: high = time-sensitive or from a manager; low = optional.
- action_type must be exactly one of: "reply", "task", "meeting", "follow_up".
- title: Short imperative title.
- description: One-sentence detail.
- source_snippet: The exact sentence from the email this came from.
- You MUST include all these fields for every item. Return a JSON array of objects."""

def extract_actions(email_text: str, subject: str, today: str) -> list[ActionItem]:
    return client.chat.completions.create(
        model="openai/gpt-oss-20b", # Changed to a faster, highly reliable model
        response_model=list[ActionItem],
        max_retries=2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Today is {today}.\nSubject: {subject}\n\n{email_text}"},
        ],
    )