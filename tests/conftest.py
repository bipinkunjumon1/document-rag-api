import os
import sys
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Set required env BEFORE importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_rag.db")
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")
os.environ.setdefault("EMBEDDING_MODEL", "test-embedding-model")
os.environ.setdefault("CHUNK_SIZE", "50")
os.environ.setdefault("CHUNK_OVERLAP", "10")
os.environ.setdefault("TOP_K", "3")
os.environ.setdefault("MAX_UPLOAD_SIZE_MB", "5")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db import database as db_module
from app.db.database import Base
from app.db.session import get_db
from app.main import app
from app.services import embedding_service as embedding_module
from app.services import llm_service as llm_module


# ---- Test DB (SQLite in-memory, shared across connections) ----
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, future=True
)

# Patch the app's engine/session and create tables
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal
Base.metadata.create_all(bind=test_engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# ---- Fake embedding model (deterministic, no model download) ----
class _FakeEmbeddingService:
    DIM = 16

    def _vec(self, text: str) -> list[float]:
        # Deterministic vector from char codes; pad/truncate to DIM
        codes = [float((ord(c) % 97) / 97.0) for c in text[: self.DIM]]
        while len(codes) < self.DIM:
            codes.append(0.0)
        return codes

    def embed_text(self, text: str) -> list[float]:
        return self._vec(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]


@pytest.fixture(autouse=True)
def _patch_services(monkeypatch):
    fake_embed = _FakeEmbeddingService()
    monkeypatch.setattr(
        embedding_module, "get_embedding_service", lambda: fake_embed
    )
    # Also patch where it's imported in routes/qa_service
    from app.api.routes import documents as documents_route
    from app.services import qa_service as qa_mod

    monkeypatch.setattr(
        documents_route, "get_embedding_service", lambda: fake_embed
    )
    monkeypatch.setattr(qa_mod, "get_embedding_service", lambda: fake_embed)

    class _FakeLLM:
        def generate_answer(self, context: str, question: str) -> str:
            return f"MOCK_ANSWER for: {question}"

    fake_llm = _FakeLLM()
    monkeypatch.setattr(llm_module, "get_llm_service", lambda: fake_llm)
    monkeypatch.setattr(qa_mod, "get_llm_service", lambda: fake_llm)
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def api_headers() -> dict[str, str]:
    return {"X-API-Key": get_settings().API_KEY}


@pytest.fixture(autouse=True)
def _clean_db():
    """Wipe tables between tests."""
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.exec_driver_sql(f"DELETE FROM {table.name}")
