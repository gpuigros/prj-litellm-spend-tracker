"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import budget, spend
from app.config import settings
from app.database.connection import close_db, init_db
from app.exceptions import SpendAPIError

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting LLM Spend API", version="1.0.0")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down LLM Spend API")
    await close_db()


app = FastAPI(
    title=settings.app_name,
    description="Internal API for tracking LLM expenditure by developer",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for SpendAPIError
@app.exception_handler(SpendAPIError)
async def spend_api_error_handler(request: Request, exc: SpendAPIError) -> JSONResponse:
    """Handle SpendAPIError exceptions."""
    logger.warning(
        "API error",
        error=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, **exc.details},
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next) -> None:
    """Log incoming requests."""
    logger.info(
        "Incoming request",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
    )
    response = await call_next(request)
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response
    logger.error("Unhandled exception", error=str(exc), exc_info=True, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Register routes
app.include_router(spend.router, prefix="/me/spend", tags=["spend"])
app.include_router(budget.router, prefix="/me", tags=["budget"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
