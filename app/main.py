"""Application entry-point: logging, middleware, lifespan, router wiring."""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.config import settings
from app.database import Base, engine
from app.routers import addresses as addresses_router


# ---------------------------------------------------------------------------
# Logging — configured manually to avoid basicConfig conflicts on Windows
# ---------------------------------------------------------------------------

def _configure_logging() -> None:
    """Attach a formatted StreamHandler to the root logger."""
    root = logging.getLogger()

    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


_configure_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create database tables on startup; log shutdown."""
    logger.info("Starting %s", settings.APP_NAME)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")
    yield
    logger.info("Shutting down %s", settings.APP_NAME)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="A minimal address-book API.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware: log every request / response with timing ------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response

# --- Global exception handler for unhandled errors ------------------------

@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# --- Routers --------------------------------------------------------------

app.include_router(addresses_router.router, prefix="/api/v1")

# --- Health check ---------------------------------------------------------

@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Simple liveness probe for load balancers and orchestrators."""
    return {"status": "healthy"}