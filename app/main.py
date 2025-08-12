"""
Project Thalassa - FastAPI Application Entry Point

This module serves as the main entry point for the Thalassa bioinformatics
data analysis platform, providing secure file upload and dashboard functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .api.dashboard import router as dashboard_router
from .api.upload import router as upload_router
from .config import settings

app = FastAPI(
    title="Project Thalassa",
    description="Bioinformatics data analysis platform for SRS risk assessment",
    version=settings.app_version,
)

# Configure template and static file serving
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add proxy headers middleware to handle X-Forwarded-* headers from nginx
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "thalassa.intautomation.org",
            "*.intautomation.org",
            "localhost",
        ],
    )

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://thalassa.intautomation.org",
    ],  # Development origins and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Project Thalassa API is running"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "thalassa-api",
        "version": settings.app_version,
        "template_rendering": "enabled",
        "static_files": "mounted",
        "components": ["upload", "dashboard"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
