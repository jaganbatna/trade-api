import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# In-memory rate limit store: { identifier: [timestamp, ...] }
RATE_LIMIT_STORE: dict[str, list[float]] = {}

# Config
MAX_REQUESTS = 10          # max requests per window
WINDOW_SECONDS = 60        # sliding window in seconds
ANALYZE_MAX_REQUESTS = 5   # stricter limit for /analyze endpoint
ANALYZE_WINDOW = 60


def _get_identifier(request: Request) -> str:
    """Use session_id if available, else fall back to IP."""
    session_id = getattr(request.state, "session_id", None)
    if session_id:
        return f"session:{session_id}"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    return f"ip:{request.client.host}"


def _is_rate_limited(identifier: str, max_requests: int, window: int) -> tuple[bool, int]:
    now = time.time()
    cutoff = now - window

    timestamps = RATE_LIMIT_STORE.get(identifier, [])
    # Keep only timestamps in the current window
    timestamps = [t for t in timestamps if t > cutoff]
    RATE_LIMIT_STORE[identifier] = timestamps

    if len(timestamps) >= max_requests:
        retry_after = int(window - (now - timestamps[0])) + 1
        return True, retry_after

    timestamps.append(now)
    RATE_LIMIT_STORE[identifier] = timestamps
    return False, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health/docs endpoints
        path = request.url.path
        if path in ("/", "/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        identifier = _get_identifier(request)

        # Stricter limits for analyze endpoint
        if "/analyze/" in path:
            limited, retry_after = _is_rate_limited(
                f"analyze:{identifier}", ANALYZE_MAX_REQUESTS, ANALYZE_WINDOW
            )
        else:
            limited, retry_after = _is_rate_limited(
                identifier, MAX_REQUESTS, WINDOW_SECONDS
            )

        if limited:
            logger.warning(f"Rate limit exceeded for {identifier} on {path}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "error_code": "RATE_LIMITED",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
