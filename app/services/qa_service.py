from __future__ import annotations
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.qa import AnswerResponse
from app.services.embedding_service import get_embedding_service
from app.services.llm_service import get_llm_service
from app.services.retrieval_service import RetrievalService

logger = get_logger(__name__)


class QAService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = get_embedding_service()
        self.llm_service = get_llm_service()
        self.retrieval_service = RetrievalService(db)

    def answer(self, question: str) -> AnswerResponse:
        logger.info(f"QA request question_chars={len(question)}")
        query_embedding = self.embedding_service.embed_text(question)
        top = self.retrieval_service.top_chunks(
            query_embedding, k=self.settings.TOP_K
        )

        if not top:
            return AnswerResponse(
                question=question,
                answer="I don't know based on the provided documents.",
                sources=[],
            )

        context_parts = [chunk.chunk_text for chunk, _ in top]
        context = "\n\n---\n\n".join(context_parts)
        answer_text = self.llm_service.generate_answer(context, question)

        return AnswerResponse(
            question=question,
            answer=answer_text,
            sources=context_parts,
        )
