"""Tests for logging and monitoring middleware."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.middleware.logging_middleware import RequestLoggingMiddleware, ResponseHeaderMiddleware

@pytest.fixture
def test_app():
    """Create a test FastAPI application with middleware."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ResponseHeaderMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    @app.get("/error")
    def error_endpoint():
        raise ValueError("Test error")
    
    return app

@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)

def test_request_logging_middleware_success(client):
    """Test successful request logging."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    
def test_request_logging_middleware_error(client):
    """Test error request logging."""
    with pytest.raises(ValueError):
        client.get("/error")

def test_response_headers_middleware(client):
    """Test response headers."""
    response = client.get("/test")
    
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
