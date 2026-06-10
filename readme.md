# Document RAG API

Production-style **Retrieval-Augmented Generation (RAG)** API built with FastAPI, PostgreSQL, and Gemini 2.5 Flash. Upload documents, automatically embed them, and ask natural-language questions answered from your own content.

---

## 1. Project Overview

This service lets users:

1. Upload TXT / PDF documents.
2. Automatically extract text, chunk it, and embed each chunk with `sentence-transformers/all-MiniLM-L6-v2`.
3. Persist documents and chunk embeddings in PostgreSQL (embeddings stored as JSON, no `pgvector`).
4. Ask questions — the service embeds the query, retrieves the top-K most similar chunks via cosine similarity computed in Python (NumPy), and passes the context to **Gemini 2.5 Flash** to generate a grounded answer.

It is intentionally simple, deployable to Railway in minutes, and ships without Docker, Redis, Celery, or any external vector database.

---

## 2. Architecture

```
┌──────────────┐     upload      ┌──────────────────┐     embed     ┌──────────────────────┐
│   Client     │ ───────────────▶│  FastAPI Routes  │ ─────────────▶│ SentenceTransformer  │
└──────────────┘                 └──────────────────┘               └──────────────────────┘
       │                                  │                                  │
       │ ask question                     │ persist                          │ vectors
       ▼                                  ▼                                  ▼
┌──────────────┐                 ┌──────────────────┐               ┌──────────────────────┐
│   FastAPI    │ ─── retrieve ──▶│  PostgreSQL      │◀── chunks ────│  Repositories        │
│   QA route   │                 │  (JSON column)   │               └──────────────────────┘
└──────────────┘                 └──────────────────┘
       │                                  ▲
       │ top-K cosine (NumPy)             │
       ▼                                  │
┌──────────────┐                          │
│ Gemini 2.5   │ ── answer ───────────────┘
│   Flash      │
└──────────────┘
```

Clean layered architecture: **routes → services → repositories → db**.

---

## 3. Features

- Upload TXT and PDF documents.
- Word-based chunking with configurable size and overlap.
- Local embeddings (no external embedding API).
- Cosine similarity retrieval in pure Python/NumPy.
- Gemini 2.5 Flash answer generation with a strict context-only prompt.
- API key authentication on all endpoints except `/health`.
- Global error handling with a consistent `{success, message}` envelope.
- Structured logging for uploads, retrieval, and LLM calls.
- Alembic migrations.
- Pytest suite with mocked Gemini and embeddings — zero external calls.

---

## 4. Tech Stack

| Layer        | Choice                                        |
|--------------|-----------------------------------------------|
| API          | FastAPI, Uvicorn                              |
| Language     | Python 3.11                                   |
| DB           | PostgreSQL                                    |
| ORM          | SQLAlchemy 2.0 (`Mapped` / `mapped_column`)   |
| Migrations   | Alembic                                       |
| Validation   | Pydantic V2 + pydantic-settings               |
| LLM          | Gemini 2.5 Flash (`google-generativeai`)      |
| Embeddings   | `sentence-transformers/all-MiniLM-L6-v2`      |
| PDF parsing  | `pypdf`                                       |
| Tests        | Pytest + FastAPI `TestClient`                 |
| Deploy       | Railway (Nixpacks + Procfile)                 |

---

## 5. Installation

Requires Python 3.11 and a running PostgreSQL instance.

```bash
git clone <your-repo-url>
cd <repo>
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Environment Variables

Copy and edit:

```bash
cp .env.example .env
```

| Variable             | Required | Default                                          | Description                                |
|----------------------|----------|--------------------------------------------------|--------------------------------------------|
| `DATABASE_URL`       | yes      | —                                                | SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/rag_db` |
| `API_KEY`            | yes      | —                                                | Value clients must send in `X-API-Key`     |
| `GEMINI_API_KEY`     | yes      | —                                                | Google AI Studio API key                   |
| `GEMINI_MODEL`       | no       | `gemini-2.5-flash`                               | Gemini model name                          |
| `EMBEDDING_MODEL`    | no       | `sentence-transformers/all-MiniLM-L6-v2`         | HuggingFace model id                       |
| `CHUNK_SIZE`         | no       | `500`                                            | Words per chunk                            |
| `CHUNK_OVERLAP`      | no       | `50`                                             | Word overlap between chunks                |
| `TOP_K`              | no       | `5`                                              | Chunks retrieved per question              |
| `MAX_UPLOAD_SIZE_MB` | no       | `10`                                             | Upload limit                               |

---

## 7. Running Locally

```bash
uvicorn app.main:app --reload
```

Swagger UI: <http://localhost:8000/docs>

---

## 8. Database Setup

Create a local Postgres database:

```bash
createdb rag_db
```

Or via `psql`:

```sql
CREATE DATABASE rag_db;
```

Set `DATABASE_URL` in `.env` accordingly.

---

## 9. Running Migrations

```bash
alembic upgrade head
```

To create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

## 10. Running Tests

Tests use SQLite in-memory and mock both Gemini and the embedding model — no network or model download required.

```bash
pytest -v
```

---

## 11. API Documentation

Interactive Swagger UI: `/docs`
OpenAPI JSON: `/openapi.json`

![Swagger UI](docs/screenshots/swagger.png)

### Endpoints

| Method | Path                              | Auth | Description                       |
|--------|-----------------------------------|------|-----------------------------------|
| GET    | `/health`                         | no   | Liveness check                    |
| POST   | `/api/v1/documents/upload`        | yes  | Upload TXT/PDF and index it       |
| GET    | `/api/v1/documents`               | yes  | List uploaded documents           |
| GET    | `/api/v1/documents/{id}`          | yes  | Document details                  |
| POST   | `/api/v1/qa/ask`                  | yes  | Ask a question                    |

---

## 12. Example Requests

Health:

```bash
curl http://localhost:8000/health
```

Upload a TXT file:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-API-Key: $API_KEY" \
  -F "file=@./notes.txt"
```

List documents:

```bash
curl http://localhost:8000/api/v1/documents \
  -H "X-API-Key: $API_KEY"
```

Get one document:

```bash
curl http://localhost:8000/api/v1/documents/<document_id> \
  -H "X-API-Key: $API_KEY"
```

Ask a question:

```bash
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the deployment requirements?"}'
```

![QA Response](docs/screenshots/qa.png)

---

## 13. Railway Deployment Guide

1. Push this repository to GitLab/GitHub.
2. Go to <https://railway.app> → **New Project** → **Deploy from Repo**.
3. Add the **PostgreSQL** plugin. Railway exposes `DATABASE_URL` automatically; prefix it with `postgresql+psycopg2://` if Railway provides only `postgresql://`.
4. In **Variables**, set:
   - `API_KEY`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL` (optional)
   - `EMBEDDING_MODEL` (optional)
   - `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_UPLOAD_SIZE_MB` (optional)
5. Railway detects `Procfile` and `railway.json`. The pre-deploy command `alembic upgrade head` runs migrations on every deploy.
6. After the first deploy, open the generated URL → `/docs` to verify.

> **Note:** the first request triggers a one-time download of the embedding model (~90 MB). If cold-start latency matters, consider pre-warming via a startup hook or a larger instance.

![Railway Deploy](docs/screenshots/railway.png)

---

## 14. Future Improvements

- Switch to `pgvector` (or a managed vector DB) once corpus size grows beyond a few thousand chunks.
- Stream responses from Gemini for better UX.
- Add re-ranking (e.g. cross-encoder) on top of cosine retrieval.
- Per-document scoping in `/qa/ask` (`document_ids` filter).
- Background job for large uploads instead of synchronous embedding.
- Rate limiting and per-user API keys.
- Citations with chunk IDs and offsets, not just chunk text.
- OpenTelemetry tracing for retrieval and LLM spans.

---

## 15. Folder Structure

```
.
├── app/
│   ├── main.py
│   ├── api/routes/{health,documents,qa}.py
│   ├── core/{config,security,logging,exceptions}.py
│   ├── db/{database,session,models}.py
│   ├── schemas/{document,qa,response}.py
│   ├── repositories/{document_repository,chunk_repository}.py
│   ├── services/{embedding_service,llm_service,document_parser,chunking_service,retrieval_service,qa_service}.py
│   └── utils/similarity.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/0001_initial.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_upload.py
│   └── test_qa.py
├── alembic.ini
├── Procfile
├── railway.json
├── requirements.txt
├── .env.example
└── README.md
```

---

## Interview Explanation: Why this architecture was chosen

**Layered separation (routes → services → repositories → db).** Each layer has one responsibility. Routes only handle HTTP concerns, services hold business logic, repositories own SQL. This is easy to reason about, easy to test, and easy to swap out (e.g. replacing the retrieval store later).

**JSON-stored embeddings + Python cosine similarity.** The brief explicitly excludes `pgvector` and vector DBs. JSON storage keeps the schema portable and the dependency surface minimal. For a take-home corpus this is more than fast enough; the `RetrievalService` is the only place that would change when migrating to `pgvector` or a managed vector DB later.

**Local SentenceTransformer embeddings.** Removes an external dependency and cost during indexing, gives deterministic vectors, and runs anywhere Python runs.

**Gemini 2.5 Flash with a strict context-only prompt.** Flash is fast and cheap, ideal for a single-turn RAG response. The prompt explicitly tells the model to answer "I don't know" when context is insufficient — reducing hallucinations.

**Pydantic V2 + SQLAlchemy 2.0.** Modern, typed, and the de-facto standard. `pydantic-settings` cleanly loads configuration from `.env`.

**Alembic migrations.** Required for any production-grade service; included from day one so schema evolution is tracked.

**Tests with mocked Gemini and embeddings.** Fast, deterministic, no network, no model download — they run in CI in seconds.

**Railway over Docker.** Matches the brief's "no Docker" rule. `Procfile` + `railway.json` give a reproducible deploy with migrations on every release.
