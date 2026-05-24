# AI Code & Crypto API

A production-ready REST API offering **code analysis**, **live crypto tracking**, and **remote job search** — powered by free public data sources. No API keys required for the underlying data.

## 🚀 Live Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/info` | API info and available endpoints |
| `GET /api/v1/crypto/balance/{address}` | BTC wallet balance (Mempool.space) |
| `GET /api/v1/crypto/prices` | Live BTC/ETH prices (CoinGecko) |
| `GET /api/v1/crypto/fees` | BTC fee estimates |
| `GET /api/v1/jobs/search?q=python` | Search remote jobs (3 sources) |
| `GET /api/v1/jobs/remote` | Latest remote jobs |
| `POST /api/v1/code/review` | AI code quality review |
| `GET /api/v1/usage` | API usage statistics |

## Quick Start

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then visit: http://localhost:8000/docs for interactive Swagger docs.

## Docker

```bash
cd backend
docker build -t ai-code-api .
docker run -p 8000:8000 ai-code-api
```

## Deploy to Render (Free)

1. Push to GitHub
2. Go to render.com - New Web Service
3. Connect your repo - Render auto-detects render.yaml
4. Deploy!

## Tech Stack

- FastAPI + Uvicorn
- Python 3.9
- Pydantic models
- OpenAPI/Swagger auto-docs
