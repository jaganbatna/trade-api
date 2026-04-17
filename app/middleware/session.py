import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

# In-memory session store: { session_id: {created_at, last_request, request_count} }
SESSION_STORE: dict[str, dict] = {}

SESSION_COOKIE = "trade_session_id"
SESSION_TTL_SECONDS = 3600  # 1 hour


def get_or_create_session(request: Request) -> str:
    session_id = request.cookies.get(SESSION_COOKIE)

    now = time.time()

    if session_id and session_id in SESSION_STORE:
        session = SESSION_STORE[session_id]
        # Expire old sessions
        if now - session["created_at"] > SESSION_TTL_SECONDS:
            del SESSION_STORE[session_id]
            session_id = None
        else:
            session["last_request"] = now
            session["request_count"] += 1
            logger.info(f"Session {session_id[:8]}... | request #{session['request_count']}")
            return session_id

    # Create new session
    session_id = str(uuid.uuid4())
    SESSION_STORE[session_id] = {
        "created_at": now,
        "last_request": now,
        "request_count": 1,
    }
    logger.info(f"New session created: {session_id[:8]}...")
    return session_id


def get_session_data(session_id: str) -> dict | None:
    return SESSION_STORE.get(session_id)


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = get_or_create_session(request)
        request.state.session_id = session_id

        response = await call_next(request)

        # Set cookie if not present
        if not request.cookies.get(SESSION_COOKIE):
            response.set_cookie(
                key=SESSION_COOKIE,
                value=session_id,
                httponly=True,
                max_age=SESSION_TTL_SECONDS,
                samesite="lax",
            )

        return response
