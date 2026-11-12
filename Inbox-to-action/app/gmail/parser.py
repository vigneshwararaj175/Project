import base64
from bs4 import BeautifulSoup

def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

def extract_plain_text(payload) -> str:
    mime = payload.get("mimeType")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            return _decode(data)
    if mime == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            return BeautifulSoup(_decode(data), "html.parser").get_text(" ")
    for part in payload.get("parts", []):
        text = extract_plain_text(part)
        if text:
            return text
    return ""