# Edge Case Handling Guide: AI Discovery Engine

This document outlines the potential edge cases for the **AI Discovery Engine** across ingestion, clustering, extraction, and synthesis phases, and provides the corresponding mitigation strategies.

---

## 1. Data Ingestion Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **API Rate Limits** (Reddit, YouTube) | Ingestion script halts or gets IP-blocked. | Implement exponential backoff, request throttling, and queue workers (Celery/Redis) to spread requests. |
| **App Store RSS Feed Changes** | Ingestion of App Store reviews fails due to structural changes in Apple's XML/JSON. | Implement a fallback scraping parser (e.g., using `app-store-scraper` or RSS backup pages) and add automated health-check alerts. |
| **Non-English Input** | Non-English text fails translation or pollutes semantic embeddings. | Integrate a lightweight language detection step (e.g., `langdetect`) and use translation APIs or Groq to translate texts to English before processing. |
| **Empty or Spam Comments** | High volume of "nice", "good product", or emoji-only posts dilute analytical value. | Filter out comments where word count < 3, and strip standalone non-standard Unicode emojis during sanitization. |

---

## 2. AI & Clustering Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Outlier Comments (Noise)** | Comments that don't fit any theme skew cluster shapes. | Use **HDBSCAN** for clustering, which inherently tags outliers as `-1` (noise) rather than forcing them into clusters. |
| **Giant Cluster Dominance** | One massive generic cluster (e.g. general "sale interest") hides smaller, valuable sub-themes. | Apply hierarchical clustering or re-cluster dominant groups independently (sub-clustering) to extract finer-grained insights. |
| **Token Limit Exceeded** | Extraordinarily long Reddit threads exceed vector embedding or LLM context window limits. | Implement text chunking with overlapping windows (e.g., 500-token chunks with 50-token overlap) to summarize or embed sections. |

---

## 3. Groq API & LLM Extraction Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Groq Rate Limits (TPM/RPM)** | Batch extraction fails mid-way due to Groq's high-speed API limits. | Implement client-side token bucket limiting and batch retries. Use LLaMA-3.1-8B-Instant for simple extractions to conserve limits. |
| **Malformed LLM JSON Output** | Python script fails to parse output when LLM returns invalid JSON structures or extra markdown tags. | Force JSON outputs using **Groq Tool Use / Function Calling** or Pydantic validation (via libraries like `instructor`). |
| **Dual/Conflicting Intents** | A comment contains multiple barriers (e.g., "Love the price but the size is too large"). | Prompt the extraction model to return barriers as a list of distinct objects rather than a single string. |
| **Hallucinated Attributes** | LLM extracts motivations/barriers not present in the text. | Refine system prompts with strict constraints: *"Base your extraction ONLY on the provided text. Do not assume or extrapolate."* |

---

## 4. Privacy & Compliance Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **PII Leakage** | User usernames, email addresses, or phone numbers are sent to external LLMs. | Run a local Named Entity Recognition (NER) pipeline (via Spacy) to redact names, emails, and phone numbers *before* sending payload to Groq. |
| **Private Data Ingestion** | Ingestion of private forum posts or closed fashion groups. | Enforce strict platform boundaries: only ingest publicly indexed resources (Google Play, Apple App Store, public Subreddits). |
