from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date

class ActionItem(BaseModel):
    title: str = Field(description="Short imperative title, e.g. 'Send Q4 budget to Priya'")
    description: str = Field(description="One-sentence detail")
    action_type: Literal["reply", "task", "meeting", "follow_up"]
    due_date: Optional[date] = None
    priority: Literal["high", "medium", "low"]
    source_snippet: str = Field(description="Sentence from the email this came from")