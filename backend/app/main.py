from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
import traceback

from .config import get_settings
from .routers import documents_router, chat_router, whatsapp_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs("media", exist_ok=True)

app = FastAPI(
    title="RAG Agent API",
    description="AI-powered RAG system for product catalog queries",
    version="1.0.0",
)


# Global exception handler - catches all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with structured error response."""
    error_id = id(exc)  # Unique error identifier for log correlation
    logger.error(
        f"Unhandled exception [error_id={error_id}]: {type(exc).__name__}: {exc}\n"
        f"Path: {request.url.path}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal error occurred. Please try again.",
            "error_code": "INTERNAL_ERROR",
            "error_id": str(error_id),
        },
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media (category images)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include routers
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(whatsapp_router)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "RAG Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "documents": "/documents",
            "chat": "/chat",
            "whatsapp": "/whatsapp",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from .services import VectorStoreService

    vector_store = VectorStoreService()
    collection_info = vector_store.get_collection_info()

    return {
        "status": "healthy",
        "vector_store": collection_info,
    }
