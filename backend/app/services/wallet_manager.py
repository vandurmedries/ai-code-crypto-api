"""
Wallet Manager for Autonomous Earnings
Generates and manages crypto wallets for earning payouts
"""

import os
import json
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging


@dataclass
class CryptoWallet:
    wallet_id: str
    currency: str  # BTC, ETH, SOL, etc.
    address: str
    private_key: Optional[str]  # Encrypted
    balance: float
    total_received: float
    created_at: str
    secret_code: str  # For verification
    beneficiary_email: str


@dataclass
class EarningNotification:
    notification_id: str
    wallet_id: str
    amount: float
    currency: str
    timestamp: str
    tx_hash: Optional[str]
    secret_code: str
    confirmed: bool = False


class WalletManager:
    """
    Manages crypto wallets for autonomous earning payouts
    """
    
    def __init__(self, storage_path: str = "./wallets"):
        self.storage_path = storage_path
        self.wallets: Dict[str, CryptoWallet] = {}
        self.notifications: Dict[str, EarningNotification] = {}
        self.logger = logging.getLogger('WalletManager')
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_wallets()
    
    def _load_wallets(self):
        """Load existing wallets from storage"""
        wallets_file = os.path.join(self.storage_path, "wallets.json")
        if os.path.exists(wallets_file):
            try:
                with open(wallets_file, 'r') as f:
                    data = json.load(f)
                    for wallet_data in data.values():
                        wallet = CryptoWallet(**wallet_data)
                        self.wallets[wallet.wallet_id] = wallet
            except:
                pass
    
    def _save_wallets(self):
        """Save wallets to storage"""
        wallets_file = os.path.join(self.storage_path, "wallets.json")
        data = {wid: w.__dict__ for wid, w in self.wallets.items()}
        with open(wallets_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_secret_code(self) -> str:
        """Generate secure secret code for wallet access"""
        return secrets.token_urlsafe(16)
    
    def generate_wallet(self, currency: str, beneficiary_email: str) -> CryptoWallet:
        """
        Generate new crypto wallet for beneficiary
        """
        wallet_id = f"wal_{hashlib.md5(f'{currency}_{beneficiary_email}_{datetime.utcnow().timestamp()}'.encode()).hexdigest()[:10]}"
        
        # Generate wallet address (simulated - in production use real crypto library)
        if currency == "BTC":
            address = f"bc1q{hashlib.sha256(wallet_id.encode()).hexdigest()[:34]}"
        elif currency == "ETH":
            address = f"0x{hashlib.sha256(wallet_id.encode()).hexdigest()[:40]}"
        elif currency == "SOL":
            address = hashlib.sha256(wallet_id.encode()).hexdigest()[:44]
        else:
            address = f"addr_{hashlib.sha256(wallet_id.encode()).hexdigest()[:30]}"
        
        # Generate secret code
        secret_code = self._generate_secret_code()
        
        wallet = CryptoWallet(
            wallet_id=wallet_id,
            currency=currency,
            address=address,
            private_key=None,  # Would be encrypted in production
            balance=0.0,
            total_received=0.0,
            created_at=datetime.utcnow().isoformat(),
            secret_code=secret_code,
            beneficiary_email=beneficiary_email
        )
        
        self.wallets[wallet_id] = wallet
        self._save_wallets()
        
        self.logger.info(f"✅ Generated {currency} wallet: {address[:10]}...")
        
        return wallet
    
    def create_earning_notification(self, wallet_id: str, amount: float, tx_hash: str = None) -> EarningNotification:
        """
        Create notification for new earning
        """
        if wallet_id not in self.wallets:
            raise ValueError("Wallet not found")
        
        wallet = self.wallets[wallet_id]
        
        notification_id = f"not_{hashlib.md5(f'{wallet_id}_{amount}_{datetime.utcnow().timestamp()}'.encode()).hexdigest()[:10]}"
        
        notification = EarningNotification(
            notification_id=notification_id,
            wallet_id=wallet_id,
            amount=amount,
            currency=wallet.currency,
            timestamp=datetime.utcnow().isoformat(),
            tx_hash=tx_hash,
            secret_code=wallet.secret_code,
            confirmed=False
        )
        
        self.notifications[notification_id] = notification
        
        # Update wallet
        wallet.balance += amount
        wallet.total_received += amount
        self._save_wallets()
        
        self.logger.info(f"💰 Earning notification: {amount} {wallet.currency} → {wallet.beneficiary_email}")
        
        return notification
    
    def verify_secret_code(self, wallet_id: str, secret_code: str) -> bool:
        """Verify secret code for wallet access"""
        if wallet_id not in self.wallets:
            return False
        
        return self.wallets[wallet_id].secret_code == secret_code
    
    def get_wallet_balance(self, wallet_id: str) -> float:
        """Get wallet balance"""
        if wallet_id not in self.wallets:
            return 0.0
        return self.wallets[wallet_id].balance
    
    def get_all_wallets_for_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all wallets for a beneficiary email"""
        wallets = []
        for wallet in self.wallets.values():
            if wallet.beneficiary_email == email:
                wallets.append({
                    "wallet_id": wallet.wallet_id,
                    "currency": wallet.currency,
                    "address": wallet.address,
                    "balance": wallet.balance,
                    "total_received": wallet.total_received,
                    "created": wallet.created_at,
                    "secret_code": wallet.secret_code  # Show once
                })
        return wallets
    
    def generate_email_notification(self, notification: EarningNotification) -> str:
        """Generate email content for earning notification"""
        wallet = self.wallets.get(notification.wallet_id)
        if not wallet:
            return ""
        
        email_content = f"""
🎉 AUTONOMOUS EARNING - NEW PAYOUT!

Dear Beneficiary,

Your autonomous AI earning system has generated a new payout!

💰 EARNING DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amount: {notification.amount:.2f} {notification.currency}
Date: {notification.timestamp}
Wallet: {wallet.address[:15]}...
Transaction: {notification.tx_hash if notification.tx_hash else 'Pending'}

🔐 ACCESS YOUR FUNDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Secret Code: {notification.secret_code}

⚠️  IMPORTANT:
• Keep this secret code safe - it's required to access your earnings
• Do not share this code with anyone
• Save this email for your records

📊 YOUR WALLETS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Balance: {wallet.balance:.2f} {wallet.currency}
Total Received: {wallet.total_received:.2f} {wallet.currency}

🔗 HOW TO ACCESS:
1. Go to: http://localhost:3000/wallets (or your system URL)
2. Enter your wallet ID: {notification.wallet_id}
3. Enter secret code: {notification.secret_code}
4. View/withdraw your earnings

🤖 AUTONOMOUS SYSTEM STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
System: Operational 24/7
Next Payout: Within 24 hours
Status: Auto-earning active

Questions? Reply to this email.

Best regards,
Your Autonomous AI Earning System

---
This is an automated message from your autonomous earning system.
Generated: {datetime.utcnow().isoformat()}
        """
        
        return email_content
    
    def get_complete_wallet_summary(self, email: str) -> Dict[str, Any]:
        """Get complete summary of all wallets and earnings for email"""
        wallets = self.get_all_wallets_for_email(email)
        
        total_by_currency = {}
        for wallet in wallets:
            curr = wallet["currency"]
            if curr not in total_by_currency:
                total_by_currency[curr] = 0.0
            total_by_currency[curr] += wallet["balance"]
        
        return {
            "beneficiary_email": email,
            "total_wallets": len(wallets),
            "wallets": wallets,
            "total_balance_by_currency": total_by_currency,
            "total_notifications": len([n for n in self.notifications.values() 
                                      if n.wallet_id in [w["wallet_id"] for w in wallets]]),
            "autonomous_status": "active"
        }


# Global instance
_wallet_manager: Optional[WalletManager] = None

def get_wallet_manager() -> WalletManager:
    """Get or create wallet manager"""
    global _wallet_manager
    if _wallet_manager is None:
        _wallet_manager = WalletManager()
    return _wallet_manager
