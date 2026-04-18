import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Depends, Path

from app.models.schemas import AnalysisResponse, ErrorResponse
from app.middleware.auth import verify_api_key
from app.services.validator import validate_sector
from app.services.search import search_market_data
from app.services.gemini import generate_analysis
from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

router = APIRouter()

CACHE_TTL = 1800  # 30 minutes


@router.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    summary="Analyze a sector for trade opportunities",
    description=(
        "Accepts an Indian market sector name and returns a structured markdown "
        "report with trade opportunities, export/import insights, government "
        "schemes, and investment outlook. Results are cached for 30 minutes."
    ),
    responses={
        200: {"description": "Successful analysis report"},
        400: {"model": ErrorResponse, "description": "Invalid sector name"},
        401: {"model": ErrorResponse, "description": "Missing API key"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal error"},
        503: {"model": ErrorResponse, "description": "AI service unavailable"},
    },
)
async def analyze_sector(
    request: Request,
    sector: str = Path(..., min_length=2, max_length=60),
    _: str = Depends(verify_api_key),
) -> AnalysisResponse:

    session_id = getattr(request.state, "session_id", "unknown")
    logger.info(f"[{session_id[:8]}] Analyze request for sector: '{sector}'")

    # ---------------- VALIDATION ----------------
    try:
        clean_sector = validate_sector(sector)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ---------------- CACHE ----------------
    cache_key = f"report:{clean_sector}"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Serving cached report for '{clean_sector}'")
        cached["session_id"] = session_id
        return AnalysisResponse(**cached)

    # ---------------- SEARCH ----------------
    try:
        logger.info(f"Searching data for '{clean_sector}'...")
        search_data = await search_market_data(clean_sector)
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        search_data = {}

    sources_count = sum(len(v) for v in search_data.values())

    # ---------------- AI ----------------
    try:
        logger.info(f"Calling AI for '{clean_sector}'...")
        report_md = await generate_analysis(clean_sector, search_data)

        if not report_md or len(report_md.strip()) < 50:
            raise ValueError("AI returned empty or weak response")

    except ValueError as e:
        # Known issue (like missing API key)
        logger.error(f"AI VALUE ERROR: {str(e)}")
        raise HTTPException(status_code=503, detail=f"AI ERROR: {str(e)}")

    except Exception as e:
        # REAL DEBUG INFO
        logger.error(f"AI CRASH: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"AI ERROR: {str(e)}")

    # ---------------- RESPONSE ----------------
    payload = {
        "sector": clean_sector,
        "session_id": session_id,
        "generated_at": datetime.now(timezone.utc),
        "report_markdown": report_md,
        "sources_used": sources_count,
    }

    cache_set(
        cache_key,
        {**payload, "generated_at": payload["generated_at"].isoformat()},
        ttl=CACHE_TTL,
    )

    return AnalysisResponse(**payload)