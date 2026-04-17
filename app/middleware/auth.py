import os
import logging
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

logger = logging.getLogger(__name__)

API_KEY = os.getenv("TRADE_API_KEY", "trade-secret-key-2024")

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    header_key: Optional[str] = Security(api_key_header),
) -> str:
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