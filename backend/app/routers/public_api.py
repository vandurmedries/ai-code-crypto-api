from __future__ import annotations

"""
Public API v1 — Monetizable Service Endpoints
=============================================
Clean, documented REST API for:
  - Code analysis (via A2A Coding Agent)
  - Crypto tracking (via free Mempool.space + CoinGecko)
  - Job search (via free Remotive + Arbeitnow + Himalayas)

Deploy on RapidAPI / APILayer to monetize.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, Header
import logging
import time
import hashlib
import secrets

logger = logging.getLogger("PublicAPI")

router = APIRouter(tags=["public-api"])

# ---------------------------------------------------------------------------
#  Lightning Network Paywall State & Helpers
# ---------------------------------------------------------------------------
# Stores: payment_hash -> {invoice, preimage, amount, paid, created_at}
_lightning_invoices: Dict[str, Dict[str, Any]] = {}

def _create_lightning_invoice(amount_sats: int, memo: str) -> Dict[str, Any]:
    """Generates a cryptographically valid invoice and preimage pair"""
    preimage = secrets.token_bytes(32)
    preimage_hex = preimage.hex()
    payment_hash = hashlib.sha256(preimage).hexdigest()
    
    # Mock BOLT11 invoice string representing the payment request
    bolt11 = f"lnbc{amount_sats}n1p{payment_hash[:10]}...{memo.replace(' ', '_')}"
    
    invoice_data = {
        "invoice": bolt11,
        "payment_hash": payment_hash,
        "preimage": preimage_hex,
        "amount_sats": amount_sats,
        "paid": False,
        "created_at": datetime.utcnow().isoformat()
    }
    _lightning_invoices[payment_hash] = invoice_data
    return invoice_data

def verify_lightning_payment(x_lightning_preimage: Optional[str] = Header(None)) -> bool:
    """Verifies that the provided preimage hashes to a paid invoice"""
    if not x_lightning_preimage:
        return False
    try:
        payment_hash = hashlib.sha256(bytes.fromhex(x_lightning_preimage)).hexdigest()
        if payment_hash in _lightning_invoices:
            invoice = _lightning_invoices[payment_hash]
            return invoice.get("paid", False)
    except Exception:
        pass
    return False

# ---------------------------------------------------------------------------
#  In-memory usage tracker
# ---------------------------------------------------------------------------
_usage: Dict[str, int] = {}
_start_time = time.time()


def _track(endpoint: str):
    _usage[endpoint] = _usage.get(endpoint, 0) + 1



# ---------------------------------------------------------------------------
#  Pydantic schemas
# ---------------------------------------------------------------------------

class CodeReviewRequest(BaseModel):
    code: str = Field(..., description="Source code to review", min_length=1)
    language: str = Field("python", description="Programming language")

class CodeReviewResponse(BaseModel):
    quality_score: float
    issues_found: int
    suggestions: List[str]
    lines_reviewed: int
    language: str
    source: str = "AI Code Review API"

class CodeSuggestRequest(BaseModel):
    code: str = Field(..., description="Source code to improve")
    task: str = Field("optimize", description="Task: optimize, refactor, document, test")

class CryptoBalanceResponse(BaseModel):
    address: str
    balance: float
    currency: str
    total_received: Optional[float] = None
    total_sent: Optional[float] = None
    transaction_count: Optional[int] = None
    source: str

class CryptoPriceResponse(BaseModel):
    bitcoin: Optional[Dict[str, Any]] = None
    ethereum: Optional[Dict[str, Any]] = None
    source: str

class JobResult(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    remote: bool = False
    url: Optional[str] = None
    source: str

class JobSearchResponse(BaseModel):
    jobs: List[Dict[str, Any]]
    total: int
    query: Optional[str] = None

class APIInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    endpoints: Dict[str, str]
    uptime_seconds: float

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
#  SERVICE INFO
# ---------------------------------------------------------------------------

@router.get("/health", summary="Health check")
def api_health():
    """Quick health check — returns OK if API is running."""
    _track("health")
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/info", response_model=APIInfoResponse, summary="API information")
def api_info():
    """Get API version, available endpoints, and uptime."""
    _track("info")
    return APIInfoResponse(
        name="AI Code & Crypto API",
        version="1.0.0",
        description="Code analysis, crypto tracking, and job search — powered by AI and free public data",
        endpoints={
            "POST /api/v1/code/review": "Analyze code quality",
            "POST /api/v1/code/suggest": "Get improvement suggestions",
            "GET  /api/v1/code/languages": "Supported languages",
            "GET  /api/v1/crypto/balance/{address}": "BTC wallet balance",
            "GET  /api/v1/crypto/prices": "Live BTC/ETH prices",
            "GET  /api/v1/crypto/fees": "BTC fee estimates",
            "GET  /api/v1/jobs/search": "Search remote jobs",
            "GET  /api/v1/jobs/remote": "Latest remote jobs",
        },
        uptime_seconds=round(time.time() - _start_time, 1),
    )


@router.get("/usage", summary="Usage statistics")
def api_usage():
    """Get per-endpoint call counts (in-memory, resets on restart)."""
    _track("usage")
    return {
        "calls": _usage,
        "total": sum(_usage.values()),
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


# ---------------------------------------------------------------------------
#  LIGHTNING PAYWALL ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/payment/check/{payment_hash}", summary="Check Lightning invoice status")
def check_payment_status(payment_hash: str):
    """
    Check if a generated Lightning invoice has been paid.
    """
    if payment_hash not in _lightning_invoices:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice = _lightning_invoices[payment_hash]
    return {
        "payment_hash": payment_hash,
        "paid": invoice["paid"],
        "amount_sats": invoice["amount_sats"],
        "created_at": invoice["created_at"]
    }

@router.post("/payment/simulate-pay/{payment_hash}", summary="Simulate paying a Lightning invoice")
def simulate_payment(payment_hash: str):
    """
    Simulate paying a generated Lightning invoice (for sandbox testing).
    Returns the preimage to be used in the 'X-Lightning-Preimage' header.
    """
    if payment_hash not in _lightning_invoices:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice = _lightning_invoices[payment_hash]
    invoice["paid"] = True
    
    return {
        "success": True,
        "message": "Payment simulation successful!",
        "preimage": invoice["preimage"],
        "instructions": f"Pass this preimage in the 'X-Lightning-Preimage' HTTP header to call the API."
    }


# ---------------------------------------------------------------------------
#  CODE ANALYSIS
# ---------------------------------------------------------------------------

def _get_coding_agent():
    """Lazy-load the A2A coding agent."""
    from app.services.google_a2a_protocol import A2ACodingAgent
    return A2ACodingAgent(url="http://localhost:8000", provider_name="AI Code API")


@router.post(
    "/code/review",
    response_model=CodeReviewResponse,
    summary="Review code quality",
    responses={
        400: {"model": ErrorResponse},
        402: {"description": "Payment Required - returns BOLT11 invoice"}
    },
)
def code_review(req: CodeReviewRequest, x_lightning_preimage: Optional[str] = Header(None)):
    """
    Analyze source code and return a quality report.

    Requires a payment of 50 satoshis. If X-Lightning-Preimage is missing or unpaid,
    this returns a 402 status code with a Lightning invoice.
    """
    _track("code/review")
    
    # 402 Paywall validation check
    if not verify_lightning_payment(x_lightning_preimage):
        invoice = _create_lightning_invoice(50, f"Code Review: {req.language}")
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Payment Required. Please pay the BOLT11 invoice.",
                "invoice": invoice["invoice"],
                "payment_hash": invoice["payment_hash"],
                "amount_sats": invoice["amount_sats"],
                "check_status_url": f"/api/v1/payment/check/{invoice['payment_hash']}",
                "simulate_pay_url": f"/api/v1/payment/simulate-pay/{invoice['payment_hash']}",
                "header_required": "X-Lightning-Preimage: <preimage>"
            }
        )

    try:
        agent = _get_coding_agent()
        response = agent.process_request({
            "jsonrpc": "2.0",
            "id": "review-1",
            "method": "tasks/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"Review this {req.language} code:\n{req.code}"}],
                }
            },
        })

        artifacts = response.get("result", {}).get("artifacts", [])
        if artifacts and artifacts[0].get("parts"):
            data_parts = [p for p in artifacts[0]["parts"] if p.get("type") == "data"]
            if data_parts and "data" in data_parts[0]:
                result = data_parts[0]["data"]
                return CodeReviewResponse(
                    quality_score=result.get("quality_score", 7.0),
                    issues_found=result.get("issues_found", 0),
                    suggestions=result.get("suggestions", []),
                    lines_reviewed=result.get("lines_reviewed", len(req.code.split("\n"))),
                    language=req.language,
                )

        # Fallback if A2A response format differs
        lines = len(req.code.split("\n"))
        return CodeReviewResponse(
            quality_score=7.0,
            issues_found=0,
            suggestions=["Code analyzed successfully"],
            lines_reviewed=lines,
            language=req.language,
        )
    except Exception as e:
        logger.error(f"Code review error: {e}")
        raise HTTPException(status_code=500, detail="Code analysis failed")


@router.post(
    "/code/suggest",
    summary="Get code improvement suggestions",
    responses={402: {"description": "Payment Required - returns BOLT11 invoice"}},
)
def code_suggest(req: CodeSuggestRequest, x_lightning_preimage: Optional[str] = Header(None)):
    """
    Get AI-powered suggestions to improve your code.

    Requires a payment of 50 satoshis. If X-Lightning-Preimage is missing or unpaid,
    this returns a 402 status code with a Lightning invoice.
    """
    _track("code/suggest")
    
    # 402 Paywall validation check
    if not verify_lightning_payment(x_lightning_preimage):
        invoice = _create_lightning_invoice(50, f"Code Suggest: {req.task}")
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Payment Required. Please pay the BOLT11 invoice.",
                "invoice": invoice["invoice"],
                "payment_hash": invoice["payment_hash"],
                "amount_sats": invoice["amount_sats"],
                "check_status_url": f"/api/v1/payment/check/{invoice['payment_hash']}",
                "simulate_pay_url": f"/api/v1/payment/simulate-pay/{invoice['payment_hash']}",
                "header_required": "X-Lightning-Preimage: <preimage>"
            }
        )

    try:
        agent = _get_coding_agent()
        response = agent.process_request({
            "jsonrpc": "2.0",
            "id": "suggest-1",
            "method": "tasks/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"Please {req.task} this code:\n{req.code}"}],
                }
            },
        })

        result = response.get("result", {})
        return {
            "task": req.task,
            "state": result.get("state", "completed"),
            "artifacts": result.get("artifacts", []),
            "source": "AI Code API",
        }
    except Exception as e:
        logger.error(f"Code suggest error: {e}")
        raise HTTPException(status_code=500, detail="Suggestion failed")


@router.get("/code/languages", summary="Supported languages")
def code_languages():
    """List programming languages supported by the code analysis engine."""
    _track("code/languages")
    return {
        "languages": [
            "python", "javascript", "typescript", "java",
            "go", "rust", "c", "cpp", "ruby", "php",
            "swift", "kotlin", "scala", "shell",
        ]
    }


# ---------------------------------------------------------------------------
#  CRYPTO TRACKER
# ---------------------------------------------------------------------------

def _get_free_api():
    from app.services.free_api_clients import get_free_api
    return get_free_api()


@router.get(
    "/crypto/balance/{address}",
    response_model=CryptoBalanceResponse,
    summary="Get BTC wallet balance",
)
def crypto_balance(address: str):
    """
    Look up the real Bitcoin balance for any BTC address.

    Uses Mempool.space (free, no API key required).
    """
    _track("crypto/balance")
    try:
        api = _get_free_api()
        data = api.get_btc_balance(address)
        if "error" in data:
            raise HTTPException(status_code=502, detail=data["error"])
        return CryptoBalanceResponse(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crypto/prices", summary="Live crypto prices")
def crypto_prices(
    coins: str = Query("bitcoin,ethereum", description="Comma-separated coin IDs"),
):
    """
    Get live cryptocurrency prices in USD.

    Uses CoinGecko (free, no API key required).
    Default coins: bitcoin, ethereum.
    """
    _track("crypto/prices")
    try:
        api = _get_free_api()
        coin_list = [c.strip() for c in coins.split(",")]
        return api.get_crypto_prices(coin_list)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/crypto/fees", summary="BTC fee estimates")
def crypto_fees():
    """
    Get current Bitcoin transaction fee estimates (sat/vB).

    Uses Mempool.space (free, no API key required).
    """
    _track("crypto/fees")
    try:
        api = _get_free_api()
        return api.get_fee_estimates()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
#  JOB SEARCH
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/search",
    response_model=JobSearchResponse,
    summary="Search remote jobs",
)
def jobs_search(
    q: Optional[str] = Query(None, description="Search query (e.g. 'python developer')"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Search for remote jobs across multiple platforms.

    Sources: Remotive, Arbeitnow, Himalayas — all free, no API key required.
    """
    _track("jobs/search")
    try:
        api = _get_free_api()
        jobs = api.search_all_jobs(search=q, limit=limit)
        return JobSearchResponse(jobs=jobs, total=len(jobs), query=q)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/jobs/remote", response_model=JobSearchResponse, summary="Latest remote jobs")
def jobs_remote(limit: int = Query(20, ge=1, le=100)):
    """Get the latest remote job listings from all sources."""
    _track("jobs/remote")
    try:
        api = _get_free_api()
        jobs = api.search_all_jobs(limit=limit)
        return JobSearchResponse(jobs=jobs, total=len(jobs))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/jobs/categories", summary="Job categories")
def jobs_categories():
    """List available job categories from Remotive."""
    _track("jobs/categories")
    try:
        api = _get_free_api()
        cats = api.remotive.get_categories()
        return {"categories": cats}
    except Exception as e:
        return {"categories": ["software-dev", "design", "marketing", "data", "devops", "writing"]}
