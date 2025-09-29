from dataclasses import dataclass
from typing import Dict, Any
import os, joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from src.common.text_utils import normalize

MODEL_DIR = "models/abuse"
os.makedirs(MODEL_DIR, exist_ok=True)

LABELS = ["non_abusive", "abusive", "threat"]

def train(data_csv: str = "data/samples/abuse_sample.csv"):
    df = pd.read_csv(data_csv)
    X = df["text"].apply(normalize).values
    y = df["label"].values
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("clf", LinearSVC())
    ])
    pipe.fit(X, y)
    joblib.dump(pipe, os.path.join(MODEL_DIR, "model.joblib"))
    preds = pipe.predict(X)
    rep = classification_report(y, preds, zero_division=0)
    with open(os.path.join(MODEL_DIR, "report.txt"), "w") as f:
        f.write(rep)
    return rep

def load():
    return joblib.load(os.path.join(MODEL_DIR, "model.joblib"))

def infer(text: str, pipe=None) -> Dict[str, Any]:
    if pipe is None:
        pipe = load()
    norm = normalize(text)
    pred = pipe.predict([norm])[0]
    return {"label": pred, "details": f"top_class={pred}"}
