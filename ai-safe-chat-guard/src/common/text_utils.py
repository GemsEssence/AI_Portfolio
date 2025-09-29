import re
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

URL_RE = re.compile(r"https?://\S+|www\.\S+")
USER_RE = re.compile(r"@\w+")
NUM_RE = re.compile(r"\b\d+\b")

def normalize(text: str) -> str:
    t = text.strip().lower()
    t = URL_RE.sub(" _url_ ", t)
    t = USER_RE.sub(" _user_ ", t)
    t = NUM_RE.sub(" _num_ ", t)
    t = re.sub(r"[^a-zA-Z_\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"
