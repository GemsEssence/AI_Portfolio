from collections import deque
from typing import Dict, Any
from nltk.sentiment import SentimentIntensityAnalyzer
from src.common.text_utils import normalize

class EscalationDetector:
    def __init__(self, window:int=5, negative_thresh:float=-0.3, slope_thresh:float=-0.1):
        self.window = window
        self.sia = SentimentIntensityAnalyzer()
        self.scores = deque(maxlen=window)
        self.negative_thresh = negative_thresh
        self.slope_thresh = slope_thresh

    def update(self, text:str) -> Dict[str, Any]:
        score = self.sia.polarity_scores(normalize(text))["compound"]
        self.scores.append(score)
        label = "stable"
        details = f"mean={sum(self.scores)/len(self.scores):.2f}, last={score:.2f}"
        if len(self.scores) >= 3:
            # simple slope: last - first normalized by length
            slope = (self.scores[-1] - self.scores[0]) / (len(self.scores)-1)
            mean = sum(self.scores)/len(self.scores)
            if mean < self.negative_thresh or slope < self.slope_thresh:
                label = "escalating"
                details += f", slope={slope:.2f}"
        return {"label": label, "details": details}
