import httpx
import logging
import asyncio
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

DDGO_URL = "https://api.duckduckgo.com/"
HEADERS = {"User-Agent": "TradeOpportunitiesAPI/1.0 (research bot)"}


async def _ddgo_instant(query: str, client: httpx.AsyncClient) -> list[str]:
    """DuckDuckGo Instant Answer API — returns text snippets."""
    try:
        params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
        resp = await client.get(DDGO_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        snippets = []
        if data.get("AbstractText"):
            snippets.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                snippets.append(topic["Text"])
        return snippets
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for '{query}': {e}")
        return []


async def _ddgo_html_search(query: str, client: httpx.AsyncClient) -> list[str]:
    """Scrape DuckDuckGo HTML search for more results."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        resp = await client.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        text = resp.text

        # Simple extraction of result snippets from HTML
        import re
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
        clean = []
        for s in snippets[:8]:
            s = re.sub(r"<[^>]+>", "", s).strip()
            if s and len(s) > 30:
                clean.append(s)
        return clean
    except Exception as e:
        logger.warning(f"DuckDuckGo HTML search failed for '{query}': {e}")
        return []


async def search_market_data(sector: str) -> dict[str, list[str]]:
    """
    Run multiple targeted searches for the given sector and return
    a dict of { topic: [snippets] }.
    """
    queries = {
        "market_overview": f"{sector} sector India market overview 2024 2025",
        "trade_opportunities": f"India {sector} export import trade opportunities 2025",
        "government_policy": f"India government policy scheme {sector} sector 2024 2025",
        "fdi_investment": f"FDI investment {sector} India recent news",
        "challenges": f"{sector} industry India challenges competition global",
        "top_companies": f"top companies {sector} sector India BSE NSE",
    }

    results: dict[str, list[str]] = {}

    async with httpx.AsyncClient() as client:
        tasks = []
        keys = []
        for key, query in queries.items():
            tasks.append(_ddgo_html_search(query, client))
            tasks.append(_ddgo_instant(query, client))
            keys.append(key)

        raw = await asyncio.gather(*tasks, return_exceptions=True)

    # Merge html + instant results per topic
    for i, key in enumerate(keys):
        html_res = raw[i * 2] if not isinstance(raw[i * 2], Exception) else []
        instant_res = raw[i * 2 + 1] if not isinstance(raw[i * 2 + 1], Exception) else []
        combined = list(dict.fromkeys(html_res + instant_res))  # deduplicate
        results[key] = combined[:6]  # cap per topic

    total = sum(len(v) for v in results.values())
    logger.info(f"Collected {total} snippets across {len(results)} topics for '{sector}'")
    return results
