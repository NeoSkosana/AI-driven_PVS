"""Middleware for logging and monitoring."""
import time
from typing import Callable
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..monitoring.metrics import MetricsService

logger = logging.getLogger(__name__)
metrics = MetricsService()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request information and performance metrics."""
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware."""
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log information."""
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else None
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log request information
            logger.info(
                f"Request: {method} {url} from {client_host} "
                f"- Status: {response.status_code} "
                f"- Processing Time: {process_time:.3f}s"
            )
            
            # Add custom headers for monitoring
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error information
            logger.error(
                f"Error processing request: {method} {url} from {client_host} "
                f"- Error: {str(e)}"
            )
            raise

class ResponseHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security and monitoring headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security and monitoring headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
