import re
import logging

logger = logging.getLogger(__name__)

# Allowed sector keywords (non-exhaustive; validation is regex-based)
KNOWN_SECTORS = [
    "pharmaceuticals", "technology", "agriculture", "automotive",
    "textiles", "chemicals", "steel", "energy", "renewable energy",
    "fintech", "healthcare", "defence", "aerospace", "electronics",
    "food processing", "gems and jewellery", "it services",
    "telecom", "logistics", "real estate", "education", "tourism",
    "banking", "insurance", "retail", "ecommerce", "media",
    "mining", "oil and gas", "construction", "biotechnology",
]

MAX_LENGTH = 60
MIN_LENGTH = 2
# Only letters, spaces, digits, hyphens allowed
VALID_PATTERN = re.compile(r"^[a-zA-Z0-9 \-]+$")


def validate_sector(sector: str) -> str:
    """
    Validate and normalise a sector name.
    Returns cleaned sector string or raises ValueError.
    """
    sector = sector.strip()

    if len(sector) < MIN_LENGTH:
        raise ValueError(f"Sector name too short (min {MIN_LENGTH} characters).")
    if len(sector) > MAX_LENGTH:
        raise ValueError(f"Sector name too long (max {MAX_LENGTH} characters).")
    if not VALID_PATTERN.match(sector):
        raise ValueError(
            "Sector name contains invalid characters. "
            "Only letters, numbers, spaces, and hyphens are allowed."
        )

    normalised = sector.lower().strip()
    logger.info(f"Validated sector: '{normalised}'")
    return normalised
