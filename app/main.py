import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import analyze
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.session import SessionMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Trade Opportunities API starting up...")
    yield
    logger.info("Trade Opportunities API shutting down...")


app = FastAPI(
    title="Trade Opportunities API",
    description="Analyzes market data and provides trade opportunity insights for specific sectors in India.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (order matters — added last = executed first)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SessionMiddleware)

# Routers
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Trade Opportunities API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
