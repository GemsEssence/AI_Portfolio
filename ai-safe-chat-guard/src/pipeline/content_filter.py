from typing import Dict, Any
import re
from src.rules.lexicons import AGE_TAXONOMY

def infer(text: str, user_age: int) -> Dict[str, Any]:
    """
    Determine if content is age-appropriate based on keywords and user age.
    """
    text_lower = text.lower()
    hits = []

    # Check which age buckets the text matches
    for bucket, keywords in AGE_TAXONOMY.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                hits.append((bucket, keyword))

    # Default required age
    required = "7+"

    if hits:
        # pick the strictest bucket among matches
        order = {"7+": 0, "13+": 1, "18+": 2}
        strictest_bucket = max((h[0] for h in hits), key=lambda b: order[b])
        required = strictest_bucket

    # Determine label based on user's age
    label = "allow"
    if user_age < 13 and required in ("13+", "18+"):
        label = "warn" if required == "13+" else "block"
    elif 13 <= user_age < 18 and required == "18+":
        label = "block"

    # Add details
    details = f"required={required}; hits={hits}" if hits else "no flags"

    return {"label": label, "details": details}
