import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(
        self,
        document_id: uuid.UUID,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        objects = [
            DocumentChunk(
                document_id=document_id,
                chunk_text=text,
                embedding=embedding,
            )
            for text, embedding in zip(chunks, embeddings)
        ]
        self.db.add_all(objects)
        self.db.flush()
        return len(objects)

    def list_all(self) -> list[DocumentChunk]:
        stmt = select(DocumentChunk)
        return list(self.db.execute(stmt).scalars().all())

    def list_by_document(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
        return list(self.db.execute(stmt).scalars().all())
