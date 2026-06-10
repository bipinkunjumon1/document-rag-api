from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.session import get_db
from app.schemas.qa import AnswerResponse, QuestionRequest
from app.services.qa_service import QAService

router = APIRouter(
    prefix="/api/v1/qa",
    tags=["qa"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
) -> AnswerResponse:
    service = QAService(db)
    return service.answer(payload.question)
