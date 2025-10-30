import re

def sanitize_text(text: str) -> str:
    # very simple sanitizer: trim and collapse long whitespace
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text).strip()
    # further sanitization can be added here (PHI removal, tokenization)
    return t
