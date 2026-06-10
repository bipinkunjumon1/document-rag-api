class AppException(Exception):
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)


class DocumentNotFoundError(AppException):
    status_code = 404
    message = "Document not found"


class InvalidFileError(AppException):
    status_code = 400
    message = "Invalid file"


class LLMError(AppException):
    status_code = 502
    message = "LLM service error"


class UnauthorizedError(AppException):
    status_code = 401
    message = "Invalid or missing API key"
