# Production Handover & Operations Guide

This manual provides the instructions to execute, configure, and maintain the **AI Discovery Engine** in a production environment.

---

## 1. Pipeline Execution Flow

The ingestion and clustering pipeline should run on a scheduled job (e.g. daily cron) to keep data fresh. Follow this execution order:

### Step 1: Ingest Raw Data
Downloads public reviews and comments into `data/raw/raw_feedback.json`.
```bash
python run_ingestion.py --limit 100
```

### Step 2: Semantic Clustering
Processes raw comments into vector embeddings and groups similar themes in `data/processed/clustered_feedback.json`.
```bash
python run_clustering.py
```

### Step 3: Structured Extraction & DB Synchronization
Populates structured columns (motivations, barriers, segments) and saves them into the SQLite database file (`discovery.db`).
```bash
python run_extraction.py
```

### Step 4: Launch Dashboard Interface
Starts the local Flask web server.
```bash
python app.py
```
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 2. Directory Structure & Outputs

```
AI Discovered Engine/
├── data/
│   ├── raw/
│   │   └── raw_feedback.json          # Phase 1: Sanitized feed downloads
│   └── processed/
│       └── clustered_feedback.json    # Phase 2: Grouped cluster categories
├── ingest/
│   ├── config.py                      # Credentials & environment variables
│   ├── pipeline.py                    # Cleaning & sanitization logic
│   ├── connectors/                    # Ingestion connectors (Play Store, RSS App Store)
│   └── processing/
│       ├── database.py                # SQLite database management
│       ├── embeddings.py              # Semantic embedding generation
│       └── extractor.py               # Groq LLM extraction connector
├── Design/
│   └── index.html                     # Frontend PM dashboard template
├── discovery.db                       # Active SQLite relational database
├── app.py                             # Flask web app & Opportunity prioritization backend
└── requirements.txt                   # Dependency file
```

---

## 3. Logs & Diagnostics

*   **Console Logs:** All scripts print verbose timestamps and info flags to stdout.
*   **Database Inspection:** You can open `discovery.db` with any standard SQLite viewer (e.g. DBeaver or DB Browser for SQLite) to query tables or write custom analytics SQL queries directly on:
    *   `comments`
    *   `extractions`
