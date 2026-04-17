import os
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"   # Free, fast, high quality


def _build_prompt(sector: str, search_data: dict[str, list[str]]) -> str:
    date_str = datetime.utcnow().strftime("%B %Y")

    sections = []
    for topic, snippets in search_data.items():
        if snippets:
            label = topic.replace("_", " ").title()
            body = "\n".join(f"  - {s}" for s in snippets)
            sections.append(f"### {label}\n{body}")

    context = "\n\n".join(sections) if sections else "No external data collected."

    return f"""You are a senior trade and market analyst specializing in the Indian economy.
Today's date: {date_str}

You have been asked to produce a professional market analysis report on the **{sector.upper()}** sector in India.

Below is raw market intelligence gathered from public web sources:

---
{context}
---

Using the above data (and your own knowledge where data is thin), write a **comprehensive markdown report** with exactly this structure:

# 🇮🇳 India Trade Opportunities Report: {sector.title()} Sector

## Executive Summary
(3-4 sentences summarising the sector's position and key opportunities)

## Market Overview
- Current market size (estimate if needed)
- Growth rate (CAGR)
- Key market segments

## Top Trade Opportunities
(List at least 4 specific opportunities, each with a brief rationale)

## Export Potential
- Top export destinations for Indian {sector} products
- Export value trends
- Competitive advantage India holds

## Import Landscape
- Key imported goods/materials
- Opportunities for import substitution

## Government Initiatives & Policies
- Relevant schemes (PLI, Make in India, etc.)
- Regulatory environment
- Incentives for investors/exporters

## Key Challenges & Risks
- Major obstacles for traders/investors
- Global competition concerns
- Regulatory or infrastructure gaps

## Top Players in India
(5-7 major companies or players in this sector)

## Investment Outlook (2025-2027)
- FDI trends
- Projected growth areas
- Recommended sectors to watch

## Actionable Recommendations
(3-5 concrete steps a trader or investor should take)

---
*Report generated on {date_str} | Source: Trade Opportunities API | Data from public market intelligence.*

Write in a professional but accessible tone. Use bullet points and tables where helpful. Be specific with numbers where possible."""


async def generate_analysis(sector: str, search_data: dict[str, list[str]]) -> str:
    """Call Groq API (LLaMA3-70B) to generate the markdown analysis report."""

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Get a FREE key at https://console.groq.com/keys (no credit card needed)"
        )

    prompt = _build_prompt(sector, search_data)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a senior trade and market analyst specializing in the Indian economy. Always respond in well-structured Markdown.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.4,
        "max_tokens": 4096,
        "top_p": 0.9,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(GROQ_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            choices = data.get("choices", [])
            if not choices:
                raise ValueError("Groq returned no choices in response.")

            markdown = choices[0].get("message", {}).get("content", "")
            if not markdown:
                raise ValueError("Groq returned empty content.")

            logger.info(
                f"Groq analysis generated successfully for '{sector}' "
                f"({len(markdown)} chars, model={GROQ_MODEL})"
            )
            return markdown

        except httpx.HTTPStatusError as e:
            body = e.response.text[:500]
            logger.error(f"Groq API HTTP error {e.response.status_code}: {body}")
            if e.response.status_code == 401:
                raise ValueError("Groq API key is invalid. Check GROQ_API_KEY in .env")
            elif e.response.status_code == 429:
                raise ValueError("Groq rate limit exceeded. Try again shortly.")
            elif e.response.status_code == 400:
                raise ValueError(f"Groq bad request: {body}")
            raise ValueError(f"Groq API error: {e.response.status_code}")

        except httpx.TimeoutException:
            raise ValueError("Groq API timed out. Please retry.")