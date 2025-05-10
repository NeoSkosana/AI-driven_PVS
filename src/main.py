from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api_gateway.api import app as api_app
from api_gateway.auth_api import router as auth_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Problem Validation System",
        description="AI-Driven Problem Validation System for Micro-SaaS Ideas",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount the API routers
    app.mount("/api/v1", api_app)
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    
    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
