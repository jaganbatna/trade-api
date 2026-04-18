import os
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def generate_analysis(sector: str, search_data: dict) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

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

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    payload = {
        # ✅ WORKING MODELS (don’t guess randomly again)
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]