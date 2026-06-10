# AI-Powered Document Question Answering API (RAG)

## Overview

This project is an AI-powered Document Question Answering API built using FastAPI, PostgreSQL, Sentence Transformers, and Google's Gemini 2.5 Flash.

The application allows users to upload PDF or text documents and ask natural language questions about their content. Instead of sending entire documents directly to a Large Language Model, the system uses Retrieval-Augmented Generation (RAG) to retrieve the most relevant information and generate accurate, context-aware answers.

This approach improves answer quality, reduces hallucinations, and allows users to interact with their own documents through a simple REST API.

---

## Problem Statement

Large Language Models are powerful, but they do not automatically have access to private documents.

Organizations often need a way to:

* Upload internal documents
* Search information semantically
* Ask questions in natural language
* Generate answers grounded in their own content

This project solves that problem by combining semantic search and LLM-based answer generation.

---

## Key Features

### Document Upload & Processing

* Upload PDF and TXT files
* Automatic text extraction
* Configurable document chunking

### Semantic Search

* Local embedding generation using Sentence Transformers
* Cosine similarity search using NumPy
* Retrieval of top relevant chunks

### AI Question Answering

* Gemini 2.5 Flash integration
* Context-aware answer generation
* Retrieval-Augmented Generation (RAG)

### Backend Engineering

* FastAPI REST APIs
* PostgreSQL persistence
* SQLAlchemy ORM
* Alembic migrations
* API Key authentication
* Structured logging
* Railway deployment

---

## How the System Works

### Step 1: Upload Document

A user uploads a PDF or TXT document.

### Step 2: Text Extraction

The application extracts text from the uploaded file.

### Step 3: Chunking

The extracted text is divided into smaller chunks.

### Step 4: Embedding Generation

Each chunk is converted into vector embeddings using:

Sentence Transformer:
`all-MiniLM-L6-v2`

### Step 5: Storage

Document metadata and embeddings are stored in PostgreSQL.

### Step 6: Question Answering

When a question is submitted:

1. The question is embedded.
2. Similar document chunks are retrieved.
3. Top relevant chunks are selected.
4. Context is sent to Gemini 2.5 Flash.
5. Gemini generates a grounded answer.

---

## Architecture

User
↓
Upload Document
↓
FastAPI
↓
Document Parsing
↓
Chunking
↓
Sentence Transformers
↓
PostgreSQL Storage
↓
Question
↓
Embedding Search
↓
Top-K Retrieval
↓
Gemini 2.5 Flash
↓
Answer

---

## Technology Stack

| Layer             | Technology            |
| ----------------- | --------------------- |
| Backend           | FastAPI               |
| Language          | Python 3.11           |
| Database          | PostgreSQL            |
| ORM               | SQLAlchemy            |
| Validation        | Pydantic              |
| Migrations        | Alembic               |
| Embeddings        | Sentence Transformers |
| Similarity Search | NumPy                 |
| LLM               | Gemini 2.5 Flash      |
| Deployment        | Railway               |
| Testing           | Pytest                |

---

## API Endpoints

### Health Check

GET /health

Verifies that the application is running.

---

### Upload Document

POST /api/v1/documents/upload

Uploads and indexes a document.

---

### List Documents

GET /api/v1/documents

Returns uploaded documents.

---

### Document Details

GET /api/v1/documents/{document_id}

Returns document information.

---

### Ask Question

POST /api/v1/qa/ask

Example:

```json
{
  "question": "What technologies are used in this project?"
}
```

---

## Local Setup

### Clone Repository

```bash
git clone <repository-url>
cd document-rag-api
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/rag_db

API_KEY=your_api_key

GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=gemini-2.5-flash
```

### Run Database Migrations

```bash
alembic upgrade head
```

### Start Server

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Deployment

The application is deployed on Railway.

Deployment includes:

* FastAPI Application
* PostgreSQL Database
* Environment Variable Management
* Automatic CI/CD from GitHub

---

## Testing

Run tests:

```bash
pytest -v
```

---


---

