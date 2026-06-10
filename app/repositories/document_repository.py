import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, filename: str, content: str) -> Document:
        document = Document(filename=filename, content=content)
        self.db.add(document)
        self.db.flush()
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        stmt = select(Document).where(Document.id == document_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[tuple[Document, int]]:
        stmt = (
            select(Document, func.count(DocumentChunk.id))
            .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], int(row[1] or 0)) for row in rows]

    def count_chunks(self, document_id: uuid.UUID) -> int:
        stmt = select(func.count(DocumentChunk.id)).where(
            DocumentChunk.document_id == document_id
        )
        return int(self.db.execute(stmt).scalar() or 0)
