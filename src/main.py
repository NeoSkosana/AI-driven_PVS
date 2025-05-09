from fastapi import FastAPI
import uvicorn
from api_gateway.api import app as api_app

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Problem Validation System",
        description="AI-Driven Problem Validation System for Micro-SaaS Ideas",
        version="1.0.0"
    )
    
    # Mount the API router
    app.mount("/api/v1", api_app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
