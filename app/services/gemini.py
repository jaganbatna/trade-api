import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def generate_analysis(sector: str, search_data: dict) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

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

    try:
        
        model = genai.GenerativeModel("gemini-1.0-pro")

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")