"""
Free API Clients — No API Key Required
========================================
Crypto:  Mempool.space (BTC), Blockchain.info (BTC), CoinGecko (prices)
Jobs:    Arbeitnow, Remotive, RemoteJobs.org, Himalayas

All endpoints are publicly accessible with IP-based rate limits.
"""

import time
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("FreeAPIClients")


# ---------------------------------------------------------------------------
#  CRYPTO — Bitcoin balance & transactions (NO KEY)
# ---------------------------------------------------------------------------

class MempoolSpaceClient:
    """
    Mempool.space — open-source Bitcoin explorer API
    Docs: https://mempool.space/docs/api/rest
    Rate limit: IP-based, generous for normal use
    NO API KEY REQUIRED
    """

    BASE_URL = "https://mempool.space/api"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI-Earning-Platform/1.0"})

    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get real BTC balance — no key needed"""
        try:
            url = f"{self.BASE_URL}/address/{address}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
            spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
            balance_sat = funded - spent

            # Include mempool (unconfirmed)
            mempool_funded = data.get("mempool_stats", {}).get("funded_txo_sum", 0)
            mempool_spent = data.get("mempool_stats", {}).get("spent_txo_sum", 0)
            unconfirmed_sat = mempool_funded - mempool_spent

            tx_count = data.get("chain_stats", {}).get("tx_count", 0)

            return {
                "address": address,
                "balance": balance_sat / 1e8,
                "balance_sat": balance_sat,
                "unconfirmed_balance": unconfirmed_sat / 1e8,
                "total_received": funded / 1e8,
                "total_sent": spent / 1e8,
                "transaction_count": tx_count,
                "currency": "BTC",
                "source": "mempool.space (free, no key)",
            }
        except requests.RequestException as e:
            logger.error(f"Mempool.space error for {address}: {e}")
            return {"error": str(e), "balance": 0, "currency": "BTC"}

    def get_address_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent BTC transactions — no key needed"""
        try:
            url = f"{self.BASE_URL}/address/{address}/txs"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            txs_raw = response.json()

            transactions = []
            for tx in txs_raw[:limit]:
                # Determine direction
                is_sender = any(
                    address in (vin.get("prevout", {}).get("scriptpubkey_address", ""),)
                    for vin in tx.get("vin", [])
                )

                amount_sat = 0
                for vout in tx.get("vout", []):
                    addr = vout.get("scriptpubkey_address", "")
                    if is_sender and addr != address:
                        amount_sat += vout.get("value", 0)
                    elif not is_sender and addr == address:
                        amount_sat += vout.get("value", 0)

                confirmed_time = tx.get("status", {}).get("block_time")

                transactions.append({
                    "tx_hash": tx.get("txid"),
                    "amount": amount_sat / 1e8,
                    "fee": tx.get("fee", 0) / 1e8,
                    "confirmations": "confirmed" if tx.get("status", {}).get("confirmed") else "pending",
                    "timestamp": datetime.fromtimestamp(confirmed_time).isoformat() if confirmed_time else None,
                    "is_sender": is_sender,
                    "currency": "BTC",
                    "source": "mempool.space",
                })

            return transactions
        except requests.RequestException as e:
            logger.error(f"Mempool.space tx error: {e}")
            return []

    def get_fee_estimates(self) -> Dict[str, Any]:
        """Get current recommended fees — no key needed"""
        try:
            url = f"{self.BASE_URL}/v1/fees/recommended"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


class BlockchainInfoClient:
    """
    Blockchain.info / Blockchain.com — fallback BTC client
    Basic endpoints have no key requirement
    """

    def get_address_balance(self, address: str) -> Dict[str, Any]:
        try:
            url = f"https://blockchain.info/balance?active={address}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json().get(address, {})

            balance_sat = data.get("final_balance", 0)
            return {
                "address": address,
                "balance": balance_sat / 1e8,
                "balance_sat": balance_sat,
                "total_received": data.get("total_received", 0) / 1e8,
                "transaction_count": data.get("n_tx", 0),
                "currency": "BTC",
                "source": "blockchain.info (free, no key)",
            }
        except requests.RequestException as e:
            logger.error(f"Blockchain.info error: {e}")
            return {"error": str(e), "balance": 0, "currency": "BTC"}


# ---------------------------------------------------------------------------
#  CRYPTO — Prices & market data (NO KEY)
# ---------------------------------------------------------------------------

class CoinGeckoClient:
    """
    CoinGecko public API — no key required
    Docs: https://docs.coingecko.com/reference/introduction
    Rate limit: ~10-30 req/min (IP-based)
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI-Earning-Platform/1.0"})
        self._last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < 2.5:  # stay well under limit
            time.sleep(2.5 - elapsed)
        self._last_request = time.time()

    def get_prices(self, coins: List[str] = None, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get current prices — no key needed"""
        self._rate_limit()
        coins = coins or ["bitcoin", "ethereum"]
        try:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                "ids": ",".join(coins),
                "vs_currencies": vs_currency,
                "include_24hr_change": "true",
                "include_market_cap": "true",
            }
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            data["source"] = "coingecko (free, no key)"
            return data
        except requests.RequestException as e:
            logger.error(f"CoinGecko price error: {e}")
            return {"error": str(e)}

    def get_coin_details(self, coin_id: str = "bitcoin") -> Dict[str, Any]:
        """Get detailed coin info — no key needed"""
        self._rate_limit()
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
            }
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "price_usd": data.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                "24h_change": data.get("market_data", {}).get("price_change_percentage_24h"),
                "ath": data.get("market_data", {}).get("ath", {}).get("usd"),
                "source": "coingecko (free, no key)",
            }
        except requests.RequestException as e:
            logger.error(f"CoinGecko detail error: {e}")
            return {"error": str(e)}


# ---------------------------------------------------------------------------
#  JOBS — Remote/freelance job listings (NO KEY)
# ---------------------------------------------------------------------------

class ArbeitnowClient:
    """
    Arbeitnow — free job API, no auth needed
    Docs: https://www.arbeitnow.com/api
    """

    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    def search_jobs(self, page: int = 1) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.BASE_URL, params={"page": page}, timeout=30)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for job in data.get("data", []):
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "location": job.get("location"),
                    "remote": job.get("remote", False),
                    "url": job.get("url"),
                    "tags": job.get("tags", []),
                    "created_at": job.get("created_at"),
                    "source": "arbeitnow (free, no key)",
                })
            return jobs
        except requests.RequestException as e:
            logger.error(f"Arbeitnow error: {e}")
            return []


class RemotiveClient:
    """
    Remotive — free remote job API
    Docs: https://remotive.com/api/remote-jobs
    """

    BASE_URL = "https://remotive.com/api/remote-jobs"

    def search_jobs(self, category: str = None, search: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            params = {"limit": limit}
            if category:
                params["category"] = category
            if search:
                params["search"] = search

            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for job in data.get("jobs", [])[:limit]:
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "location": job.get("candidate_required_location", "Remote"),
                    "remote": True,
                    "url": job.get("url"),
                    "category": job.get("category"),
                    "salary": job.get("salary", "Not specified"),
                    "job_type": job.get("job_type"),
                    "tags": job.get("tags", []),
                    "publication_date": job.get("publication_date"),
                    "source": "remotive (free, no key)",
                })
            return jobs
        except requests.RequestException as e:
            logger.error(f"Remotive error: {e}")
            return []

    def get_categories(self) -> List[str]:
        try:
            response = requests.get(f"{self.BASE_URL}/categories", timeout=15)
            response.raise_for_status()
            return [c.get("name") for c in response.json().get("jobs", [])]
        except Exception:
            return ["software-dev", "design", "marketing", "data", "devops", "writing"]


class HimalayasClient:
    """
    Himalayas — free remote job API, no key needed
    Docs: https://himalayas.app/api
    """

    BASE_URL = "https://himalayas.app/jobs/api"

    def search_jobs(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            params = {"limit": limit, "offset": offset}
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for job in data.get("jobs", [])[:limit]:
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("companyName"),
                    "location": job.get("location", "Remote"),
                    "remote": True,
                    "url": f"https://himalayas.app/jobs/{job.get('slug', '')}",
                    "categories": job.get("categories", []),
                    "seniority": job.get("seniority"),
                    "salary_min": job.get("minSalary"),
                    "salary_max": job.get("maxSalary"),
                    "source": "himalayas (free, no key)",
                })
            return jobs
        except requests.RequestException as e:
            logger.error(f"Himalayas error: {e}")
            return []


# ---------------------------------------------------------------------------
#  UNIFIED AGGREGATOR — combines all free sources
# ---------------------------------------------------------------------------

class FreeAPIAggregator:
    """
    Single entry point for all free, keyless APIs.
    Call this instead of the paid API clients when no keys are configured.
    """

    def __init__(self):
        self.mempool = MempoolSpaceClient()
        self.blockchain_info = BlockchainInfoClient()
        self.coingecko = CoinGeckoClient()
        self.arbeitnow = ArbeitnowClient()
        self.remotive = RemotiveClient()
        self.himalayas = HimalayasClient()

    # --- Crypto ---

    def get_btc_balance(self, address: str) -> Dict[str, Any]:
        """Get BTC balance — tries Mempool.space first, falls back to Blockchain.info"""
        result = self.mempool.get_address_balance(address)
        if "error" in result:
            logger.info("Mempool.space failed, falling back to Blockchain.info")
            result = self.blockchain_info.get_address_balance(address)
        return result

    def get_btc_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.mempool.get_address_transactions(address, limit)

    def get_crypto_prices(self, coins: List[str] = None) -> Dict[str, Any]:
        return self.coingecko.get_prices(coins)

    def get_fee_estimates(self) -> Dict[str, Any]:
        return self.mempool.get_fee_estimates()

    # --- Jobs ---

    def search_all_jobs(self, search: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search all free job sources in parallel-ish fashion"""
        all_jobs = []

        # Remotive (best for tech/dev)
        try:
            all_jobs.extend(self.remotive.search_jobs(search=search, limit=limit))
        except Exception as e:
            logger.warning(f"Remotive search failed: {e}")

        # Arbeitnow
        try:
            all_jobs.extend(self.arbeitnow.search_jobs())
        except Exception as e:
            logger.warning(f"Arbeitnow search failed: {e}")

        # Himalayas
        try:
            all_jobs.extend(self.himalayas.search_jobs(limit=limit))
        except Exception as e:
            logger.warning(f"Himalayas search failed: {e}")

        return all_jobs

    def get_status(self) -> Dict[str, Any]:
        """Quick health check of all free APIs"""
        results = {}
        try:
            self.coingecko.get_prices(["bitcoin"])
            results["coingecko"] = "✅ OK"
        except Exception:
            results["coingecko"] = "❌ Down"

        try:
            self.mempool.get_fee_estimates()
            results["mempool_space"] = "✅ OK"
        except Exception:
            results["mempool_space"] = "❌ Down"

        try:
            jobs = self.remotive.search_jobs(limit=1)
            results["remotive"] = f"✅ OK ({len(jobs)} jobs)"
        except Exception:
            results["remotive"] = "❌ Down"

        try:
            jobs = self.arbeitnow.search_jobs()
            results["arbeitnow"] = f"✅ OK ({len(jobs)} jobs)"
        except Exception:
            results["arbeitnow"] = "❌ Down"

        results["api_keys_needed"] = "NONE — all endpoints are free"
        return results


# Singleton
_free_api: Optional[FreeAPIAggregator] = None


def get_free_api() -> FreeAPIAggregator:
    """Get the free API aggregator singleton"""
    global _free_api
    if _free_api is None:
        _free_api = FreeAPIAggregator()
    return _free_api
