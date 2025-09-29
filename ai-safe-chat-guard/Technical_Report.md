# AI Safety Models POC – Technical Report

**Author:** Your Name  
**Date:** 2025-08-29

## 1. Overview & Goals

This POC implements four safety capabilities for a conversational platform:
1) Abuse Language Detection, 2) Escalation Pattern Recognition, 3) Crisis Intervention, 4) Content Filtering.
The system favors **CPU-only**, **low-latency**, **interpretable** approaches and demonstrates **end-to-end** flow from preprocessing to inference and actioning.

## 2. High-level Architecture

- **Input stream (chat messages)** → **Normalizer** (lang detect, tokenize, lower, emoji/text normalization) →  
  **Safety Orchestrator** (runs abuse, crisis, escalation, content filters) → **Policy Router** (apply thresholds, user age profile) →  
  **Actions** (block, warn, throttle, escalate-to-human, or allow).

- Models:
  - Abuse & Crisis: TF–IDF + Linear SVM/LogReg
  - Escalation: Rolling sentiment (VADER) + aggression trend detection
  - Content Filtering: Rule-based taxonomy (age 7+/13+/18+) with simple confidence

- **Interfaces**: CLI simulator (real-time), optional FastAPI service.

## 3. Data Sources & Preprocessing

- Uses **sample datasets** shipped in `data/samples/` (synthetic & paraphrased).  
- Recommended public datasets for scaling:
  - Jigsaw Toxic Comment Classification (Kaggle)
  - HateXplain (multi-annotator)
  - Crisis-related corpora (e.g., CLPsych shared tasks, RSDD for depression signals)  
  - Age-appropriateness heuristics from content rating guidelines (e.g., ESRB/MPAA-inspired keywords)

**Preprocessing**: lowercasing, URL/user/number masking, punctuation stripping, basic lemmatization (optional), language detection fallback to English-only models (others → rule-only).

## 4. Model Architectures & Training

- **Abuse**: `TfidfVectorizer(1-2 grams, min_df=2)` + Linear SVM. Labels: `non_abusive`, `abusive`, `threat`.  
- **Crisis**: `TfidfVectorizer(1-2 grams)` + Logistic Regression. Labels: `none`, `self_harm`, `suicidal_ideation`.
- **Escalation**: Rolling window (last 5 messages) sentiment mean + delta; detects `escalating` if mean < threshold and downward slope or rising aggression count.
- **Content Filter**: Keyword/regex taxonomy mapped to age buckets: `7+`, `13+`, `18+`. Produces reasons/snippets.

**Why not BERT?** Stronger accuracy, but heavier CPU latency. For POC, classic models are **fast**, **interpretable**, and **good baselines**. A drop-in HF model can be added later via the same interfaces.

## 5. Evaluation

Scripts compute **precision/recall/F1** and confusion matrices on the sample sets. Thresholds are calibrated on a validation split to target higher recall for crisis, balanced F1 for abuse.

## 6. Real-time & Integration

- CLI simulates streaming input and prints colored decisions with rationales.  
- Optional FastAPI returns JSON with all model outputs and policy action in \<50ms average on CPU for short texts (tested locally).

## 7. Ethics, Bias & Safety-by-Design

- **Bias**: term-sensitive false positives minimized with allowlists (reclaimed slurs, identity mentions in neutral contexts).  
- **Fairness checks** (placeholder): subgroup slices, threshold per-group if necessary; document results.  
- **Human-in-the-loop**: escalation triggers human review; rate-limit automated blocks; audit logs.  
- **Privacy**: process ephemeral message text, store only hashed session IDs and model outputs for metrics.

## 8. Leadership & Iteration Plan

- Milestones: (1) Baselines + plumbing, (2) Expanded datasets + HF models, (3) Fairness evals, (4) A/B in shadow mode, (5) Gradual rollouts.  
- Team roles: Data (curation, labeling), Modeling, Platform (APIs & latency), Safety Policy, Evaluation (offline + online).  
- Documentation + postmortems for threshold changes.

## 9. Results (sample data)

See `src/eval/*` outputs after running training. On tiny samples (for demo), F1 is not meaningful; purpose is wiring + methodology.

## 10. Future Work

- Multilingual models, transformer baselines, richer context (conversation graphs), active learning loops, differential privacy for logs, comprehensive fairness dashboards.

