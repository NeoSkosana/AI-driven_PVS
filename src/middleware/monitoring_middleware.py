"""Middleware for request monitoring, logging, and error tracking."""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ..monitoring.metrics import MetricsManager
from ..utils.logging_config import get_logger, set_correlation_id

logger = get_logger(__name__)

class MonitoringMiddleware(BaseHTleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics = MetricsManager()
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Add correlation ID to response headers
        start_time = time.time()
        
        # Structure request data for logging
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "correlation_id": correlation_id
        }
        
        logger.info(
            f"Incoming request",
            extra={
                "request_data": request_data,
                "correlation_id": correlation_id
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_request_duration(
                method=request.method,
                endpoint=request.url.path,
                start_time=start_time
            )
            
            # Record request count
            self.metrics.http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "response_status": response.status_code,
                    "duration": duration,
                    "correlation_id": correlation_id
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            return response
            
        except Exception as e:
            # Record error metrics
            self.metrics.record_error(
                error_type=type(e).__name__,
                location=f"{request.method}:{request.url.path}"
            )
            
            # Log error
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                    "error_details": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            
            raise  # Re-raise the exception for FastAPI's error handlers
