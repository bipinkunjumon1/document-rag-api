from __future__ import annotations


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Word-based chunking with overlap.

    `size` and `overlap` are expressed in words. Empty chunks are dropped.
    """
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0 or overlap >= size:
        overlap = max(0, min(overlap, size - 1))

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = size - overlap
    for start in range(0, len(words), step):
        window = words[start : start + size]
        if not window:
            break
        chunk = " ".join(window).strip()
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):
            break
    return chunks
