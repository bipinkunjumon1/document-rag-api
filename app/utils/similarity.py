from collections.abc import Sequence
import numpy as np


def cosine_similarity(
    v1: Sequence[float] | np.ndarray,
    v2: Sequence[float] | np.ndarray,
) -> float:
    a = np.asarray(v1, dtype=np.float32)
    b = np.asarray(v2, dtype=np.float32)
    if a.size == 0 or b.size == 0 or a.shape != b.shape:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def top_k_by_similarity(
    query: Sequence[float] | np.ndarray,
    candidates: list[tuple[object, Sequence[float]]],
    k: int = 5,
) -> list[tuple[object, float]]:
    """Score every candidate and return top-k (item, score) descending."""
    scored = [
        (item, cosine_similarity(query, embedding))
        for item, embedding in candidates
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
