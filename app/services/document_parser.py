from __future__ import annotations
import io
from app.core.exceptions import InvalidFileError

ALLOWED_EXTENSIONS = {".txt", ".pdf"}


def _extract_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return file_bytes.decode("latin-1")
        except Exception as exc:
            raise InvalidFileError("Unable to decode text file") from exc


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                parts.append(page_text)
        return "\n".join(parts)
    except InvalidFileError:
        raise
    except Exception as exc:
        raise InvalidFileError(f"Failed to parse PDF: {exc}") from exc


def extract_text(filename: str, file_bytes: bytes) -> str:
    name = (filename or "").lower().strip()
    ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileError(
            f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    if ext == ".txt":
        text = _extract_txt(file_bytes)
    else:
        text = _extract_pdf(file_bytes)
    text = text.strip()
    if not text:
        raise InvalidFileError("Document contains no extractable text")
    return text
