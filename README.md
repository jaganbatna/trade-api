# 🇮🇳 Trade Opportunities API

A **FastAPI** service that analyses market data for Indian sectors and returns AI-generated trade opportunity reports in Markdown format — powered by **Google Gemini**.

---

## 📋 Features

| Feature | Details |
|---|---|
| **Single endpoint** | `GET /api/v1/analyze/{sector}` |
| **AI Analysis** | Google Gemini 2.0 Flash generates structured Markdown reports |
| **Web Search** | DuckDuckGo scraping for real-time market data |
| **Authentication** | API Key (Bearer token or `X-API-Key` header) |
| **Rate Limiting** | 5 requests/min on `/analyze`, 10 req/min globally (in-memory) |
| **Session Tracking** | Cookie-based session with 1-hour TTL |
| **Caching** | 30-minute in-memory cache per sector |
| **Input Validation** | Sanitised sector names, length + character checks |
| **Error Handling** | Structured JSON error responses with proper HTTP codes |
| **API Docs** | Auto-generated Swagger UI at `/docs` |

---

## 🚀 Quick Setup (Step-by-Step)

### Step 1 — Get a Free Gemini API Key

1. Go to → **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account (free)
3. Click **"Create API key"**
4. Copy the key — it starts with `AIzaSy...`

### Step 2 — Configure Your `.env` File

Open `.env` in the project root and replace the placeholder:

```env
GEMINI_API_KEY=AIzaSy_REPLACE_WITH_YOUR_KEY_HERE   # ← paste your key here
TRADE_API_KEY=trade-secret-key-2024                # ← the key clients send to your API
```

> **Note:** `TRADE_API_KEY` is what *callers* of your API must send. You can change it to anything secret.

### Step 3 — Install Dependencies

Make sure Python 3.10+ is installed, then run:

```powershell
# Create virtual environment (only once)
python -m venv venv

# Activate it
.\venv\Scripts\Activate

# Install packages
pip install -r requirements.txt
```

### Step 4 — Run the Server

```powershell
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Trade Opportunities API starting up...
INFO:     Application startup complete.
```

### Step 5 — Open the API Docs

Visit → **http://localhost:8000/docs**

You'll see the interactive Swagger UI where you can test the endpoint directly.

---

## 🔑 Authentication

Every request to `/api/v1/analyze/{sector}` must include your `TRADE_API_KEY`.

**Option A — HTTP Header:**
```
X-API-Key: trade-secret-key-2024
```

**Option B — Bearer Token:**
```
Authorization: Bearer trade-secret-key-2024
```

---

## 📡 API Reference

### `GET /api/v1/analyze/{sector}`

Analyse an Indian market sector and return a Markdown report.

**Path parameter:**

| Param | Type | Example |
|---|---|---|
| `sector` | string | `pharmaceuticals`, `technology`, `agriculture` |

**Example request (curl):**

```bash
curl -X GET "http://localhost:8000/api/v1/analyze/pharmaceuticals" \
     -H "X-API-Key: trade-secret-key-2024"
```

**Example response:**

```json
{
  "sector": "pharmaceuticals",
  "session_id": "3f1a2b4c-...",
  "generated_at": "2025-04-17T12:00:00Z",
  "report_markdown": "# 🇮🇳 India Trade Opportunities Report: Pharmaceuticals Sector\n\n## Executive Summary\n...",
  "sources_used": 18
}
```

The `report_markdown` field is a full Markdown document you can save as a `.md` file.

**Save report to a file (PowerShell):**

```powershell
$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analyze/pharmaceuticals" `
    -Headers @{"X-API-Key"="trade-secret-key-2024"}

$response.report_markdown | Out-File -FilePath "pharma_report.md" -Encoding UTF8
```

---

### Other Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

---

## ⚡ Rate Limits

| Endpoint | Limit |
|---|---|
| `/api/v1/analyze/*` | 5 requests per 60 seconds |
| All other endpoints | 10 requests per 60 seconds |

When exceeded, returns `HTTP 429` with a `Retry-After` header.

---

## 🏗️ Project Structure

```
trade-api/
├── run.py                      # Entry point (loads .env, starts uvicorn)
├── requirements.txt            # Python dependencies
├── .env                        # Your secrets (never commit this!)
└── app/
    ├── main.py                 # FastAPI app, middleware registration
    ├── routers/
    │   └── analyze.py          # GET /api/v1/analyze/{sector} endpoint
    ├── middleware/
    │   ├── auth.py             # API key authentication
    │   ├── rate_limiter.py     # Sliding-window rate limiting
    │   └── session.py          # Cookie-based session tracking
    ├── models/
    │   └── schemas.py          # Pydantic request/response schemas
    └── services/
        ├── gemini.py           # Gemini API integration + prompt builder
        ├── search.py           # DuckDuckGo market data collection
        ├── cache.py            # In-memory TTL cache
        └── validator.py        # Sector name validation
```

---

## 🛡️ Security Features

- **API Key Authentication** — No key = `401 Unauthorized`; wrong key = `403 Forbidden`
- **Input Validation** — Sector names: 2–60 chars, letters/numbers/hyphens/spaces only
- **Rate Limiting** — Sliding-window in-memory limiter; stricter on the AI endpoint
- **Session Management** — HttpOnly cookies, 1-hour TTL, server-side session store
- **Error Handling** — All errors return structured JSON, no stack traces leaked

---

## 🔧 Supported Sectors (examples)

Any text works, but these are well-supported:

`pharmaceuticals` · `technology` · `agriculture` · `automotive` · `textiles` · `chemicals` · `steel` · `renewable energy` · `fintech` · `healthcare` · `defence` · `aerospace` · `electronics` · `food processing` · `gems and jewellery` · `it services` · `telecom` · `logistics` · `biotechnology`

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `httpx` | Async HTTP (Gemini API + web search) |
| `pydantic` | Data validation & schemas |
| `python-dotenv` | Load `.env` config |
| `starlette` | Middleware base |

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| `503 Gemini API key is invalid` | Check `.env` — key must start with `AIzaSy` |
| `503 rate limit reached` | Your Gemini free quota is hit — wait a minute |
| `401 Missing API key` | Add `X-API-Key: trade-secret-key-2024` header |
| `403 Invalid API key` | Key doesn't match `TRADE_API_KEY` in `.env` |
| `400 Sector name contains invalid characters` | Use only letters, numbers, spaces, hyphens |
| `429 Rate limit exceeded` | Wait the seconds shown in `Retry-After` header |
