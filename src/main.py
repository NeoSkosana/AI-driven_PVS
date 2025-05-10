from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
import os
from dotenv import load_dotenv
from api_gateway.api import app as api_app
from api_gateway.auth_api import router as auth_router
from middleware.logging_middleware import RequestLoggingMiddleware, ResponseHeaderMiddleware
from utils.logging_config import setup_logging
from utils.error_handlers import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    not_found_handler,
    internal_error_handler,
)

load_dotenv()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Setup logging
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))
    
    app = FastAPI(
        title="Problem Validation System",
        description="AI-Driven Problem Validation System for Micro-SaaS Ideas",
        version="1.0.0"
    )
    
    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ResponseHeaderMiddleware)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, not_found_handler)
    app.add_exception_handler(Exception, internal_error_handler)
    
    # Mount the API routers
    app.mount("/api/v1", api_app)
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    
    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
