import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def generate_analysis(sector: str, search_data: dict) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")

    prompt = f"""
Generate a detailed trade opportunities report for the Indian {sector} sector.

Include:
- Market Overview
- Growth Trends
- Export/Import Opportunities
- Government Schemes
- Investment Outlook

Use this data if available:
{search_data}
"""

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-mini",   # ✅ Stable + cheap
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]