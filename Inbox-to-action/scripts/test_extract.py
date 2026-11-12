from dotenv import load_dotenv
load_dotenv()

from app.agent.extractor import extract_actions

sample = """
Hi there,

Could you send the Q4 report to Priya by Friday? Also let me know if
you're free to meet Tuesday at 3pm to discuss the roadmap.
The newsletter is attached for your reference.

Thanks,
Alex
"""

actions = extract_actions(sample, subject="Q4 Report", today="2026-11-12")
for a in actions:
    print(a)