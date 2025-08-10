"""
Project Thalassa - FastAPI Application Entry Point

This module serves as the main entry point for the Thalassa bioinformatics
data analysis platform, providing secure file upload and dashboard functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Project Thalassa",
    description="Bioinformatics data analysis platform for SRS risk assessment",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
    ],  # Development origins only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Project Thalassa API is running"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {"status": "healthy", "service": "thalassa-api", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
