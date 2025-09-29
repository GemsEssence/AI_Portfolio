# AI Safety Models POC

A self-contained proof-of-concept showcasing a suite of AI Safety models for a conversational platform:

- **Abuse Language Detection** (binary + severity)
- **Escalation Pattern Recognition** (rolling sentiment + aggression trend)
- **Crisis Intervention** (self-harm / crisis indicators)
- **Content Filtering** (age-appropriate categorization)

Runs fully on CPU. Includes small **sample datasets** for quick training and demo, plus scripts to evaluate and simulate real-time chat.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon stopwords punkt
```

### 1) Train models (using sample data)
```bash
# python src/train/train_abuse.py
# python src/train/train_crisis.py

python -m src.train.train_abuse
python -m src.train.train_crisis
```

### 2) Run CLI chat simulator
```bash
# python app/cli_chat.py
python -m app.cli_chat.py
```

### 3) Evaluate
```bash
# python src/eval/eval_abuse.py
# python src/eval/eval_crisis.py

python -m src.eval.eval_abuse.py
python -m src.eval.eval_crisis.py

```

### (Optional) Run REST API (Streamlit)
```bash
streamlit run app/webapp.py
```
## Repo Structure

```
ai-safety-poc/
├─ app/
│  ├─ api.py                 # FastAPI service (optional)
│  └─ cli_chat.py            # Real-time CLI chat simulator
   └─ webapp.py              # Real-time web chat simulator
├─ data/
│  └─ samples/               # Small demo datasets (safe to share)
├─ models/                   # Saved models + vectorizers
├─ src/
│  ├─ common/                # Shared utilities
│  ├─ pipeline/              # Inference pipeline orchestration
│  ├─ rules/                 # Lexicons and rule-based helpers
│  ├─ train/                 # Training scripts
│  ├─ eval/                  # Evaluation scripts
│  └─ ui/                    # Simple terminal UI helpers
├─ tests/                    # Minimal sanity tests
├─ Technical_Report.md       # 2-4 pages markdown (export to PDF)
└─ walkthrough_script.md     # Outline for your 10-min video
```
-------------------------------------------------
## Notes on Datasets

This POC ships with **tiny** sample datasets derived from public sources' schema (synthetic + paraphrased) to keep the repo lightweight and privacy-friendly. For stronger results, update `data/` via the download pointers in `Technical_Report.md` (e.g., Jigsaw Toxicity, Crisis Text Line research references, etc.), then retrain.

## Ethics & Safety

- Mitigations: calibrated thresholds, rule+ML hybrid, human-in-the-loop escalation, explicit allow/deny lists, and transparent logging.
- Privacy: no PII stored in samples; hashing for session IDs.
- Interpretability: keyword/rationale snippets surfaced in outputs.

See the Technical Report for details.
