from __future__ import annotations
from threading import Lock
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Lazy-loaded SentenceTransformer wrapper (singleton)."""

    _instance: "EmbeddingService | None" = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._model_name = get_settings().EMBEDDING_MODEL

    @classmethod
    def instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load(self) -> None:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)

    def embed_text(self, text: str) -> list[float]:
        self._load()
        assert self._model is not None
        vector = self._model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self._load()
        assert self._model is not None
        if not texts:
            return []
        vectors = self._model.encode(texts, convert_to_numpy=True, batch_size=32)
        return [v.tolist() for v in vectors]


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService.instance()
