from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
