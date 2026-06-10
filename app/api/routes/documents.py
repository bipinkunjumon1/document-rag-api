import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import DocumentNotFoundError, InvalidFileError
from app.core.logging import get_logger
from app.core.security import require_api_key
from app.db.session import get_db
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.document import (
    DocumentDetail,
    DocumentSummary,
    DocumentUploadResponse,
)
from app.services.chunking_service import chunk_text
from app.services.document_parser import extract_text
from app.services.embedding_service import get_embedding_service

logger = get_logger(__name__)
router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    settings = get_settings()

    if not file.filename:
        raise InvalidFileError("Missing filename")

    raw = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(raw) == 0:
        raise InvalidFileError("Empty file")
    if len(raw) > max_bytes:
        raise InvalidFileError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB"
        )

    logger.info(
        f"Upload received filename={file.filename} bytes={len(raw)}"
    )

    text = extract_text(file.filename, raw)
    chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    if not chunks:
        raise InvalidFileError("Document produced no chunks")

    embeddings = get_embedding_service().embed_texts(chunks)

    doc_repo = DocumentRepository(db)
    chunk_repo = ChunkRepository(db)

    document = doc_repo.create(filename=file.filename, content=text)
    chunk_repo.bulk_create(document.id, chunks, embeddings)
    db.commit()

    logger.info(
        f"Upload stored document_id={document.id} chunks={len(chunks)}"
    )

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        chunks_created=len(chunks),
    )


@router.get("", response_model=list[DocumentSummary])
async def list_documents(
    db: Session = Depends(get_db),
) -> list[DocumentSummary]:
    repo = DocumentRepository(db)
    rows = repo.list_all()
    return [
        DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            created_at=doc.created_at,
            chunk_count=count,
        )
        for doc, count in rows
    ]


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DocumentDetail:
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if doc is None:
        raise DocumentNotFoundError()
    count = repo.count_chunks(doc.id)
    preview = (doc.content or "")[:500]
    return DocumentDetail(
        id=doc.id,
        filename=doc.filename,
        created_at=doc.created_at,
        chunk_count=count,
        content_preview=preview,
    )
