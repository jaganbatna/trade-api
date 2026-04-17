# 🇮🇳 Trade Opportunities API

A FastAPI service that analyzes Indian market sectors and returns structured trade opportunity reports powered by Google Gemini AI and live web search.

---

## Features

| Feature | Detail |
|---|---|
| **AI Analysis** | Google Gemini 1.5 Flash |
| **Web Search** | DuckDuckGo (no API key needed) |
| **Auth** | API Key (Bearer token or `X-API-Key` header) |
| **Rate Limiting** | 5 requests/min on `/analyze`, 10/min globally |
| **Session Tracking** | Cookie-based in-memory sessions |
| **Caching** | 30-minute in-memory cache per sector |
| **Storage** | Fully in-memory (no database) |

---

## Project Structure

```
trade-api/
├── app/
│   ├── main.py                  # FastAPI app, middleware registration
│   ├── routers/
│   │   └── analyze.py           # GET /api/v1/analyze/{sector}
│   ├── services/
│   │   ├── search.py            # DuckDuckGo web search
│   │   ├── gemini.py            # Google Gemini AI integration
│   │   ├── cache.py             # In-memory cache
│   │   └── validator.py         # Input validation
│   ├── middleware/
│   │   ├── auth.py              # API key authentication
│   │   ├── rate_limiter.py      # Rate limiting
│   │   └── session.py           # Session tracking
│   └── models/
│       └── schemas.py           # Pydantic models
├── run.py                       # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- A free Google Gemini API key

### 2. Get a Gemini API Key (Free)

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key

### 3. Install Dependencies

```bash
# Clone / navigate to the project folder
cd trade-api

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your keys
# GEMINI_API_KEY=your_actual_key_here
# TRADE_API_KEY=your_secret_api_key
```

### 5. Run the Server

```bash
python run.py
```

The API will start at: `http://localhost:8000`

---

## API Usage

### Authentication

Every request to `/analyze` must include your API key:

**Option A — Authorization Header:**
```
Authorization: Bearer trade-secret-key-2024
```

**Option B — Custom Header:**
```
X-API-Key: trade-secret-key-2024
```

---

### Endpoint

```
GET /api/v1/analyze/{sector}
```

#### Example Requests

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analyze/pharmaceuticals" \
  -H "Authorization: Bearer trade-secret-key-2024"
```

**With httpie:**
```bash
http GET localhost:8000/api/v1/analyze/technology "Authorization: Bearer trade-secret-key-2024"
```

#### Example Sectors to Try

- `pharmaceuticals`
- `technology`
- `agriculture`
- `automotive`
- `textiles`
- `renewable energy`
- `fintech`
- `defence`

---

### Sample Response

```json
{
  "sector": "pharmaceuticals",
  "session_id": "3f7a1b2c-...",
  "generated_at": "2025-01-15T10:30:00Z",
  "sources_used": 24,
  "report_markdown": "# 🇮🇳 India Trade Opportunities Report: Pharmaceuticals Sector\n\n## Executive Summary\n..."
}
```

The `report_markdown` field contains a full markdown report you can save as a `.md` file:

```bash
# Save the report to a file
curl -s "http://localhost:8000/api/v1/analyze/pharmaceuticals" \
  -H "Authorization: Bearer trade-secret-key-2024" \
  | python -c "import sys,json; print(json.load(sys.stdin)['report_markdown'])" \
  > pharmaceuticals_report.md
```

---

### Rate Limits

| Endpoint | Limit |
|---|---|
| `/api/v1/analyze/{sector}` | 5 requests per 60 seconds |
| All other endpoints | 10 requests per 60 seconds |

When exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

---

## API Documentation

FastAPI auto-generates interactive docs:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Error Codes

| HTTP Status | Meaning |
|---|---|
| 400 | Invalid sector name |
| 401 | Missing API key |
| 403 | Wrong API key |
| 422 | Validation error (sector too long/short) |
| 429 | Rate limit exceeded |
| 503 | Gemini AI service error |
| 500 | Unexpected internal error |

---

## Architecture

```
Client Request
     │
     ▼
SessionMiddleware      ← assigns/reads session cookie
     │
     ▼
RateLimitMiddleware    ← sliding window per session/IP
     │
     ▼
Router: /analyze/{sector}
     │
     ├─► verify_api_key (auth dependency)
     ├─► validate_sector (input sanitisation)
     ├─► cache_get (return early if cached)
     ├─► search_market_data (DuckDuckGo scrape, async)
     ├─► generate_analysis (Gemini API call)
     ├─► cache_set (store result 30 min)
     └─► Return AnalysisResponse (JSON)
```

---

## Notes

- All storage is **in-memory** — data resets when the server restarts.
- Caching avoids redundant API calls for the same sector within 30 minutes.
- If DuckDuckGo search fails, the system gracefully falls back to Gemini's training data.
- The default `TRADE_API_KEY` in `.env.example` is for development only — change it before sharing.
