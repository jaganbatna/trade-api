import os
import httpx

async def generate_analysis(sector: str, search_data: dict) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set")

    # 🔥 CRITICAL FIX
    api_key = api_key.strip()

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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
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