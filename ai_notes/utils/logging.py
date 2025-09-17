import re


def redact_pii(text: str) -> str:
    if not text:
        return text
    # emails
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", text)
    # phones (very rough)
    text = re.sub(r"\b\+?\d[\d\s\-()]{6,}\b", "[phone]", text)
    return text

