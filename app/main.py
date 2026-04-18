import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.routers import analyze
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.session import SessionMiddleware


# ================== LOAD ENV ================== #
load_dotenv()  # 🔥 REQUIRED for local .env


# ================== LOGGING ================== #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ================== DEBUG ENV ================== #
# This tells you immediately if your key is missing
if os.getenv("GEMINI_API_KEY"):
    logger.info("✅ GEMINI_API_KEY loaded successfully")
else:
    logger.warning("❌ GEMINI_API_KEY NOT FOUND")


# ================== LIFESPAN ================== #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Trade Opportunities API starting...")
    yield
    logger.info("🛑 Trade Opportunities API shutting down...")


# ================== APP ================== #
app = FastAPI(
    title="Trade Opportunities API",
    description="Analyzes market data and provides trade opportunity insights for Indian sectors.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ================== MIDDLEWARE ================== #

# CORS (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(SessionMiddleware)
app.add_middleware(RateLimitMiddleware)


# ================== ROUTES ================== #
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])


# ================== HEALTH ================== #
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


# ================== GLOBAL ERROR HANDLER ================== #
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Please try again later."
        },
    )