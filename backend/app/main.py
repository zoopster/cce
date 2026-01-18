"""
Content Creation Engine - Main FastAPI application.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import sessions_router, research_router, generate_router, publish_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-agent content creation system using Anthropic's orchestrator-worker pattern",
    version="1.0.0",
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(sessions_router)
app.include_router(research_router)
app.include_router(generate_router)
app.include_router(publish_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Ensure memory directory exists
    memory_path = Path(settings.memory_base_path)
    memory_path.mkdir(parents=True, exist_ok=True)
    print(f"Memory directory initialized at: {memory_path.absolute()}")
    print("API endpoints ready:")
    print("  - Sessions: /api/sessions")
    print("  - Research: /api/sessions/{id}/research")
    print("  - Generate: /api/sessions/{id}/generate")
    print("  - Publish: /api/sessions/{id}/publish/*")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "content-creation-engine"}


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Content Creation Engine",
        "version": "1.0.0",
        "description": "Multi-agent content creation system",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "sessions": {
                "create": "POST /api/sessions",
                "get": "GET /api/sessions/{id}",
                "delete": "DELETE /api/sessions/{id}",
                "agents": "GET /api/sessions/{id}/agents",
                "versions": "GET /api/sessions/{id}/versions",
                "content": "GET /api/sessions/{id}/content"
            },
            "research": {
                "start": "POST /api/sessions/{id}/research (SSE)",
                "get_results": "GET /api/sessions/{id}/research",
                "get_synthesis": "GET /api/sessions/{id}/research/synthesis"
            },
            "generate": {
                "generate": "POST /api/sessions/{id}/generate (SSE)",
                "iterate": "POST /api/sessions/{id}/iterate (SSE)",
                "get_version": "GET /api/sessions/{id}/versions/{version}"
            },
            "publish": {
                "wordpress": "POST /api/sessions/{id}/publish/wordpress",
                "export_html": "POST /api/sessions/{id}/publish/html",
                "preview": "GET /api/sessions/{id}/preview",
                "download": "GET /api/sessions/{id}/download",
                "verify": "POST /api/sessions/{id}/verify-citations",
                "markdown": "GET /api/sessions/{id}/markdown"
            }
        }
    }
