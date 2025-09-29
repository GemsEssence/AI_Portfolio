import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from src.pipeline import crisis

if __name__ == "__main__":
    pipe = crisis.load()
    df = pd.read_csv("data/samples/crisis_sample.csv")
    preds = pipe.predict(df["text"])
    print(classification_report(df["label"], preds, zero_division=0))
    print(confusion_matrix(df["label"], preds))
