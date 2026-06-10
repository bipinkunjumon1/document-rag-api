from __future__ import annotations
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk
from app.repositories.chunk_repository import ChunkRepository
from app.utils.similarity import top_k_by_similarity


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.chunk_repo = ChunkRepository(db)

    def top_chunks(
        self, query_embedding: list[float], k: int
    ) -> list[tuple[DocumentChunk, float]]:
        chunks = self.chunk_repo.list_all()
        if not chunks:
            return []
        candidates = [(c, c.embedding) for c in chunks]
        scored = top_k_by_similarity(query_embedding, candidates, k=k)
        # Cast object back to DocumentChunk for the caller
        return [(item, score) for item, score in scored]  # type: ignore[misc]
