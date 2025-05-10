"""Error handlers and custom exceptions for the application."""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int

class AppException(Exception):
    """Base exception for application-specific errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

class ValidationException(AppException):
    """Exception for validation errors."""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class AuthenticationException(AppException):
    """Exception for authentication errors."""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class NotFoundException(AppException):
    """Exception for resource not found errors."""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

async def app_exception_handler(
    request: Request,
    exc: AppException
) -> JSONResponse:
    """Handle application-specific exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.message,
            detail=exc.detail,
            status_code=exc.status_code
        ).dict()
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    detail = str(exc)
    logger.warning(
        "Validation error",
        extra={
            "errors": exc.errors(),
            "body": exc.body,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        ).dict()
    )

async def not_found_handler(
    request: Request,
    exc: Any
) -> JSONResponse:
    """Handle 404 not found errors."""
    logger.info(
        f"Not found: {request.url.path}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="Not Found",
            detail=f"The requested resource '{request.url.path}' was not found",
            status_code=status.HTTP_404_NOT_FOUND
        ).dict()
    )

async def internal_error_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.error(
        f"Internal server error: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ).dict()
    )