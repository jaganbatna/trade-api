import time
import logging
from typing import Any

logger = logging.getLogger(__name__)

# In-memory cache: { key: (value, expires_at) }
_CACHE: dict[str, tuple[Any, float]] = {}

DEFAULT_TTL = 1800  # 30 minutes


def cache_get(key: str) -> Any | None:
    entry = _CACHE.get(key)
    if not entry:
        return None
    value, expires_at = entry
    if time.time() > expires_at:
        del _CACHE[key]
        logger.debug(f"Cache expired: {key}")
        return None
    logger.info(f"Cache hit: {key}")
    return value


def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    _CACHE[key] = (value, time.time() + ttl)
    logger.info(f"Cache set: {key} (TTL={ttl}s)")


def cache_stats() -> dict:
    now = time.time()
    active = {k: v for k, v in _CACHE.items() if v[1] > now}
    return {"active_keys": len(active), "total_keys": len(_CACHE)}
