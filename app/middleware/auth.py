import os
import logging
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Auth strategy: API Key (simple, robust for assignment scope)
#  Pass as:  Authorization: Bearer <API_KEY>
#  OR:       X-API-Key: <API_KEY>
# --------------------------------------------------------------------------- #

API_KEY = os.getenv("TRADE_API_KEY", "trade-secret-key-2024")

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    bearer: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    header_key: str | None = Security(api_key_header),
) -> str:
    """
    Accept the API key via:
      - Authorization: Bearer <key>
      - X-API-Key: <key>
    Returns the validated key on success, raises 401 on failure.
    """
    provided = None
    if bearer:
        provided = bearer.credentials
    elif header_key:
        provided = header_key

    if not provided:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide via 'Authorization: Bearer <key>' or 'X-API-Key: <key>'.",
        )

    if provided != API_KEY:
        logger.warning("Invalid API key attempt.")
        raise HTTPException(status_code=403, detail="Invalid API key.")

    return provided
