"""
Real Blockchain Wallet Integration
Uses BlockCypher API for BTC and Etherscan API for ETH
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('RealBlockchainWallet')


@dataclass
class RealWallet:
    """Represents a real crypto wallet"""
    wallet_id: str
    currency: str  # BTC, ETH
    address: str
    balance: float
    balance_wei_or_sat: int  # Raw blockchain units
    total_received: float
    total_sent: float
    transaction_count: int
    created_at: str
    last_updated: str
    beneficiary_email: str


@dataclass
class BlockchainTransaction:
    """Real blockchain transaction"""
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    timestamp: datetime
    confirmations: int
    fee: float
    status: str  # confirmed, pending


class BlockCypherClient:
    """
    BlockCypher API client for Bitcoin
    Free tier: 200 requests/day
    Docs: https://www.blockcypher.com/dev/bitcoin/
    """
    
    BASE_URL = "https://api.blockcypher.com/v1/btc/main"
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("BLOCKCYPHER_API_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Earning-Platform/1.0"
        })
    
    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get real BTC balance for an address"""
        try:
            url = f"{self.BASE_URL}/addrs/{address}/balance"
            if self.api_token:
                url += f"?token={self.api_token}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # BlockCypher returns balances in satoshis
            balance_btc = data.get("final_balance", 0) / 100_000_000
            total_received_btc = data.get("total_received", 0) / 100_000_000
            total_sent_btc = data.get("total_sent", 0) / 100_000_000
            
            return {
                "address": address,
                "balance": balance_btc,
                "balance_sat": data.get("final_balance", 0),
                "total_received": total_received_btc,
                "total_sent": total_sent_btc,
                "unconfirmed_balance": data.get("unconfirmed_balance", 0) / 100_000_000,
                "transaction_count": data.get("n_tx", 0),
                "unconfirmed_tx_count": data.get("unconfirmed_n_tx", 0),
                "currency": "BTC"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"BlockCypher API error for {address}: {e}")
            return {"error": str(e), "balance": 0, "currency": "BTC"}
    
    def get_address_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent BTC transactions for an address"""
        try:
            url = f"{self.BASE_URL}/addrs/{address}/full?limit={limit}"
            if self.api_token:
                url += f"&token={self.api_token}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for tx in data.get("txs", []):
                # Calculate amount sent/received for this address
                inputs = tx.get("inputs", [])
                outputs = tx.get("outputs", [])
                
                # Determine if this address is sending or receiving
                is_sender = any(inp.get("addresses", [])[0] == address for inp in inputs if inp.get("addresses"))
                
                amount = 0
                if is_sender:
                    # Find outputs to other addresses
                    for out in outputs:
                        if address not in out.get("addresses", []):
                            amount += out.get("value", 0) / 100_000_000
                else:
                    # Find outputs to this address
                    for out in outputs:
                        if address in out.get("addresses", []):
                            amount += out.get("value", 0) / 100_000_000
                
                transactions.append({
                    "tx_hash": tx.get("hash"),
                    "amount": amount,
                    "fee": tx.get("fees", 0) / 100_000_000,
                    "confirmations": tx.get("confirmations", 0),
                    "timestamp": datetime.fromtimestamp(tx.get("confirmed", datetime.now().timestamp())),
                    "is_sender": is_sender,
                    "currency": "BTC"
                })
            
            return transactions
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching BTC transactions: {e}")
            return []
    
    def create_webhook(self, address: str, url: str, event: str = "confirmed-tx") -> Dict[str, Any]:
        """Create webhook to get notified of new transactions"""
        try:
            webhook_url = f"{self.BASE_URL}/hooks?token={self.api_token}"
            payload = {
                "event": event,
                "address": address,
                "url": url
            }
            
            response = self.session.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating webhook: {e}")
            return {"error": str(e)}


class EtherscanClient:
    """
    Etherscan API client for Ethereum
    Free tier: 5 calls/second, 100,000 calls/day
    Docs: https://docs.etherscan.io/
    """
    
    BASE_URL = "https://api.etherscan.io/api"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ETHERSCAN_API_KEY")
        self.session = requests.Session()
    
    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get real ETH balance for an address"""
        try:
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": self.api_key
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                logger.error(f"Etherscan error: {data.get('message')}")
                return {"error": data.get("message"), "balance": 0, "currency": "ETH"}
            
            # Etherscan returns balance in Wei
            balance_wei = int(data.get("result", 0))
            balance_eth = balance_wei / 10**18
            
            return {
                "address": address,
                "balance": balance_eth,
                "balance_wei": balance_wei,
                "currency": "ETH"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Etherscan API error for {address}: {e}")
            return {"error": str(e), "balance": 0, "currency": "ETH"}
    
    def get_address_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get normal ETH transactions for an address"""
        try:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "sort": "desc",
                "apikey": self.api_key
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                return []
            
            transactions = []
            for tx in data.get("result", [])[:10]:  # Limit to 10 most recent
                amount_eth = int(tx.get("value", 0)) / 10**18
                gas_price = int(tx.get("gasPrice", 0)) / 10**9  # Gwei
                gas_used = int(tx.get("gasUsed", tx.get("gas", 0)))
                fee_eth = (gas_price * 10**9 * gas_used) / 10**18
                
                transactions.append({
                    "tx_hash": tx.get("hash"),
                    "from_address": tx.get("from"),
                    "to_address": tx.get("to"),
                    "amount": amount_eth,
                    "fee": fee_eth,
                    "confirmations": int(tx.get("confirmations", 0)),
                    "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
                    "is_sender": tx.get("from", "").lower() == address.lower(),
                    "currency": "ETH",
                    "gas_price_gwei": gas_price,
                    "gas_used": gas_used,
                    "status": "success" if tx.get("txreceipt_status") == "1" else "failed"
                })
            
            return transactions
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ETH transactions: {e}")
            return []
    
    def get_erc20_token_balance(self, token_contract: str, address: str) -> Dict[str, Any]:
        """Get ERC20 token balance (e.g., USDC, USDT)"""
        try:
            params = {
                "module": "account",
                "action": "tokenbalance",
                "contractaddress": token_contract,
                "address": address,
                "tag": "latest",
                "apikey": self.api_key
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                return {"error": data.get("message"), "balance": 0}
            
            # Get token decimals (would need another API call in production)
            # Common tokens: USDC = 6 decimals, most ERC20 = 18
            balance_raw = int(data.get("result", 0))
            
            return {
                "contract": token_contract,
                "address": address,
                "balance_raw": balance_raw,
                "currency": "ERC20"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching token balance: {e}")
            return {"error": str(e), "balance": 0}


class RealBlockchainWalletManager:
    """
    Manager for real blockchain wallets
    Integrates BlockCypher (BTC) and Etherscan (ETH) APIs
    Falls back to free keyless APIs (Mempool.space) when no keys are configured
    """
    
    def __init__(self, storage_path: str = "./wallets"):
        self.storage_path = storage_path
        self.btc_client = BlockCypherClient()
        self.eth_client = EtherscanClient()
        self.wallets: Dict[str, RealWallet] = {}
        
        # Free fallback clients — no API key needed
        self._free_btc_client = None
        try:
            from app.services.free_api_clients import MempoolSpaceClient
            self._free_btc_client = MempoolSpaceClient()
            logger.info("✅ Free BTC fallback (Mempool.space) loaded — no API key needed")
        except ImportError:
            pass
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_wallets()
    
    def _load_wallets(self):
        """Load existing wallets from storage"""
        import json
        wallets_file = os.path.join(self.storage_path, "real_wallets.json")
        if os.path.exists(wallets_file):
            try:
                with open(wallets_file, 'r') as f:
                    data = json.load(f)
                    for wallet_data in data.values():
                        wallet = RealWallet(**wallet_data)
                        self.wallets[wallet.wallet_id] = wallet
            except Exception as e:
                logger.error(f"Error loading wallets: {e}")
    
    def _save_wallets(self):
        """Save wallets to storage"""
        import json
        wallets_file = os.path.join(self.storage_path, "real_wallets.json")
        data = {wid: {
            "wallet_id": w.wallet_id,
            "currency": w.currency,
            "address": w.address,
            "balance": w.balance,
            "balance_wei_or_sat": w.balance_wei_or_sat,
            "total_received": w.total_received,
            "total_sent": w.total_sent,
            "transaction_count": w.transaction_count,
            "created_at": w.created_at,
            "last_updated": w.last_updated,
            "beneficiary_email": w.beneficiary_email
        } for wid, w in self.wallets.items()}
        
        with open(wallets_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def refresh_wallet_balance(self, wallet_id: str) -> Optional[RealWallet]:
        """Refresh wallet balance from blockchain"""
        if wallet_id not in self.wallets:
            return None
        
        wallet = self.wallets[wallet_id]
        
        try:
            if wallet.currency == "BTC":
                data = self.btc_client.get_address_balance(wallet.address)
                # Fallback to free API if BlockCypher fails (no key / rate limited)
                if "error" in data and self._free_btc_client:
                    logger.info(f"Using free Mempool.space fallback for {wallet.address[:15]}...")
                    data = self._free_btc_client.get_address_balance(wallet.address)
                if "error" not in data:
                    wallet.balance = data["balance"]
                    wallet.balance_wei_or_sat = data["balance_sat"]
                    wallet.total_received = data.get("total_received", 0)
                    wallet.total_sent = data.get("total_sent", 0)
                    wallet.transaction_count = data.get("transaction_count", 0)
                    wallet.last_updated = datetime.utcnow().isoformat()
                    
            elif wallet.currency == "ETH":
                data = self.eth_client.get_address_balance(wallet.address)
                if "error" not in data:
                    wallet.balance = data["balance"]
                    wallet.balance_wei_or_sat = data["balance_wei"]
                    wallet.last_updated = datetime.utcnow().isoformat()
                    # Get additional details from transactions
                    txs = self.eth_client.get_address_transactions(wallet.address, limit=1)
                    if txs:
                        wallet.transaction_count = len(txs)
            
            self._save_wallets()
            return wallet
            
        except Exception as e:
            logger.error(f"Error refreshing wallet {wallet_id}: {e}")
            return wallet  # Return current data even if refresh failed
    
    def get_wallet_transactions(self, wallet_id: str) -> List[Dict[str, Any]]:
        """Get real transactions for a wallet"""
        if wallet_id not in self.wallets:
            return []
        
        wallet = self.wallets[wallet_id]
        
        try:
            if wallet.currency == "BTC":
                return self.btc_client.get_address_transactions(wallet.address)
            elif wallet.currency == "ETH":
                return self.eth_client.get_address_transactions(wallet.address)
            return []
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []
    
    def add_existing_wallet(self, wallet_id: str, currency: str, address: str, beneficiary_email: str) -> RealWallet:
        """Add an existing wallet address to track"""
        wallet = RealWallet(
            wallet_id=wallet_id,
            currency=currency,
            address=address,
            balance=0.0,
            balance_wei_or_sat=0,
            total_received=0.0,
            total_sent=0.0,
            transaction_count=0,
            created_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat(),
            beneficiary_email=beneficiary_email
        )
        
        self.wallets[wallet_id] = wallet
        
        # Immediately refresh to get real balance
        self.refresh_wallet_balance(wallet_id)
        self._save_wallets()
        
        logger.info(f"✅ Added {currency} wallet: {address[:15]}...")
        return wallet
    
    def get_all_balances(self) -> Dict[str, Any]:
        """Get all wallet balances, refreshed from blockchain"""
        total_btc = 0.0
        total_eth = 0.0
        wallets_data = []
        
        for wallet_id, wallet in self.wallets.items():
            # Refresh balance
            refreshed = self.refresh_wallet_balance(wallet_id)
            if refreshed:
                if refreshed.currency == "BTC":
                    total_btc += refreshed.balance
                elif refreshed.currency == "ETH":
                    total_eth += refreshed.balance
                
                wallets_data.append({
                    "wallet_id": refreshed.wallet_id,
                    "currency": refreshed.currency,
                    "address": refreshed.address,
                    "balance": refreshed.balance,
                    "transaction_count": refreshed.transaction_count,
                    "last_updated": refreshed.last_updated
                })
        
        return {
            "total_btc": total_btc,
            "total_eth": total_eth,
            "wallets": wallets_data,
            "wallet_count": len(wallets_data),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_real_wallet_manager: Optional[RealBlockchainWalletManager] = None

def get_real_wallet_manager() -> RealBlockchainWalletManager:
    """Get or create real blockchain wallet manager"""
    global _real_wallet_manager
    if _real_wallet_manager is None:
        _real_wallet_manager = RealBlockchainWalletManager()
    return _real_wallet_manager


if __name__ == "__main__":
    # Test the real wallet integration
    import sys
    
    print("=" * 60)
    print("REAL BLOCKCHAIN WALLET INTEGRATION TEST")
    print("=" * 60)
    
    manager = RealBlockchainWalletManager()
    
    # Test with a known BTC address (Satoshi's genesis block)
    test_btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    
    print(f"\n1. Testing BTC Balance Lookup")
    print(f"   Address: {test_btc_address}")
    
    wallet = manager.add_existing_wallet(
        wallet_id="test_btc_001",
        currency="BTC",
        address=test_btc_address,
        beneficiary_email="test@example.com"
    )
    
    print(f"   Balance: {wallet.balance} BTC")
    print(f"   Transactions: {wallet.transaction_count}")
    print(f"   Last Updated: {wallet.last_updated}")
    
    # Get transactions
    print(f"\n2. Fetching Recent Transactions")
    txs = manager.get_wallet_transactions("test_btc_001")
    for tx in txs[:3]:
        print(f"   TX: {tx['tx_hash'][:20]}... Amount: {tx['amount']:.8f} BTC Confirmations: {tx['confirmations']}")
    
    # Get all balances summary
    print(f"\n3. Portfolio Summary")
    summary = manager.get_all_balances()
    print(f"   Total BTC: {summary['total_btc']}")
    print(f"   Total ETH: {summary['total_eth']}")
    print(f"   Wallets Tracked: {summary['wallet_count']}")
    
    print("\n" + "=" * 60)
    print("NOTE: To use this for real wallets:")
    print("1. Get free API keys from:")
    print("   - BlockCypher: https://www.blockcypher.com/")
    print("   - Etherscan: https://etherscan.io/apis")
    print("2. Set environment variables:")
    print("   export BLOCKCYPHER_API_TOKEN='your_token'")
    print("   export ETHERSCAN_API_KEY='your_key'")
    print("3. Add your real wallet addresses to track")
    print("=" * 60)
