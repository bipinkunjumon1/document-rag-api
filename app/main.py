from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import documents, health, qa
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Document RAG API",
    description=(
        "Production-style Retrieval-Augmented Generation API. "
        "Upload documents and ask questions about them using Gemini 2.5 Flash."
    ),
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(qa.router)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    logger.warning(f"AppException status={exc.status_code} message={exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"},
    )



@app.get("/")
def root():
    return {
        "message": "Document RAG API",
        "docs": "/docs"
    }