from __future__ import annotations
from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)

_PROMPT_TEMPLATE = """You are a helpful assistant answering questions strictly based on the provided context.

If the context does not contain enough information to answer, reply exactly: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:"""


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        self._model_name = settings.GEMINI_MODEL
        self._api_key = settings.GEMINI_API_KEY
        self._model = None

    def _client(self):
        if self._model is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self._api_key)
                self._model = genai.GenerativeModel(self._model_name)
            except Exception as exc:  # pragma: no cover - import/config failure
                logger.error(f"Failed to init Gemini client: {exc}")
                raise LLMError("Failed to initialize Gemini client") from exc
        return self._model

    def generate_answer(self, context: str, question: str) -> str:
        prompt = _PROMPT_TEMPLATE.format(context=context, question=question)
        try:
            logger.info(
                f"Calling Gemini model={self._model_name} "
                f"context_chars={len(context)} question_chars={len(question)}"
            )
            response = self._client().generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                raise LLMError("Empty response from Gemini")
            return text.strip()
        except LLMError:
            raise
        except Exception as exc:
            logger.error(f"Gemini call failed: {exc}")
            raise LLMError(f"Gemini call failed: {exc}") from exc


def get_llm_service() -> LLMService:
    return LLMService()
