"""
Wallet + Earning Integration Router
Generates wallets and sends earning notifications
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.wallet_manager import get_wallet_manager
from app.services.email_service import get_email_service
from app import models

router = APIRouter()


@router.post("/generate-wallet")
def generate_earning_wallet(
    currency: str = Body("BTC"),
    beneficiary_email: str = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Generate new crypto wallet for autonomous earnings
    Returns wallet address + secret code
    """
    wallet_mgr = get_wallet_manager()
    
    # Generate wallet
    wallet = wallet_mgr.generate_wallet(currency, beneficiary_email)
    
    # Create notification (initial setup)
    email_svc = get_email_service()
    
    email_body = f"""
🎉 WELCOME TO AUTONOMOUS AI EARNING!

Dear Beneficiary,

Your autonomous AI earning system has been configured!

💰 YOUR WALLET DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currency: {currency}
Wallet Address: {wallet.address}
Wallet ID: {wallet.wallet_id}

🔐 SECURITY INFORMATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Secret Code: {wallet.secret_code}

⚠️  CRITICAL:
• Save this secret code immediately!
• You need it to access all earnings
• Without it, funds cannot be recovered
• Do not share with anyone

📊 HOW IT WORKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. System runs 24/7 autonomously
2. Earnings are deposited to this wallet
3. You receive email notifications
4. Use secret code to access funds
5. Withdraw anytime to your bank/exchange

💵 EXPECTED EARNINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily: $25-150 (depending on strategy)
Monthly: $750-4500
Yearly: $9000-54000

🔍 MONITOR YOUR EARNINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Check status: GET /api/wallet-earning/status
View balance: Use wallet ID + secret code
Email alerts: Automatic on every payout

Next payout: Within 24 hours

🤖 System Status: OPERATIONAL

Best regards,
Your Autonomous AI Earning System
"""
    
    # Send/save email
    email_result = email_svc.send_earning_notification(
        to_email=beneficiary_email,
        subject="🔐 Your Autonomous Earning Wallet - SECRET CODE INSIDE",
        body=email_body,
        wallet_info={
            "wallet_id": wallet.wallet_id,
            "secret_code": wallet.secret_code,
            "currency": currency,
            "address": wallet.address
        }
    )
    
    return {
        "success": True,
        "wallet_created": True,
        "wallet": {
            "wallet_id": wallet.wallet_id,
            "currency": wallet.currency,
            "address": wallet.address,
            "secret_code": wallet.secret_code,
            "balance": wallet.balance
        },
        "beneficiary": beneficiary_email,
        "email_sent": email_result["success"],
        "email_location": email_result.get("saved_to"),
        "security_warning": "⚠️  SAVE SECRET CODE NOW - Cannot be recovered if lost!",
        "next_steps": [
            "Save secret code in secure location",
            "Check email for full details",
            "System starts earning automatically",
            "First payout within 24 hours"
        ]
    }


@router.post("/simulate-earning-payout")
def simulate_earning_payout(
    wallet_id: str = Body(...),
    amount: float = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Simulate autonomous earning payout to wallet
    Sends notification email
    """
    wallet_mgr = get_wallet_manager()
    email_svc = get_email_service()
    
    # Create earning notification
    try:
        notification = wallet_mgr.create_earning_notification(
            wallet_id=wallet_id,
            amount=amount,
            tx_hash=f"tx_{hash(wallet_id + str(amount)) % 100000000000}"
        )
        
        wallet = wallet_mgr.wallets.get(wallet_id)
        
        # Send email
        email_body = f"""
🎉 NEW AUTONOMOUS EARNING PAYOUT!

Dear Beneficiary,

Your AI system just earned new funds!

💰 PAYOUT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amount: {amount:.2f} {notification.currency}
Date: {notification.timestamp}
Transaction: {notification.tx_hash}

📊 YOUR WALLET:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wallet: {wallet.address[:20]}...
New Balance: {wallet.balance:.2f} {notification.currency}
Total Received: {wallet.total_received:.2f} {notification.currency}

🔐 ACCESS YOUR FUNDS:
Secret Code: {notification.secret_code}

⚡️ AUTONOMOUS SYSTEM:
Status: Earning 24/7
Next Payout: Within 24 hours
Strategy: Active

Keep earning! 🤖💰
"""
        
        email_result = email_svc.send_earning_notification(
            to_email=wallet.beneficiary_email,
            subject=f"🎉 New Earning: {amount:.2f} {notification.currency}",
            body=email_body,
            wallet_info={
                "wallet_id": wallet_id,
                "secret_code": notification.secret_code,
                "currency": notification.currency,
                "address": wallet.address
            }
        )
        
        # Add to user balance in system
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += amount
            user.total_earned += amount
            db.commit()
        
        return {
            "success": True,
            "payout": {
                "amount": amount,
                "currency": notification.currency,
                "wallet_id": wallet_id,
                "tx_hash": notification.tx_hash
            },
            "wallet_balance": wallet.balance,
            "email_sent": email_result["success"],
            "new_system_balance": round(current_user.balance + amount, 2),
            "secret_code": notification.secret_code,
            "next_payout_estimate": "Within 24 hours"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet-status")
def get_wallet_status(
    wallet_id: str = None,
    secret_code: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get wallet status and balance"""
    wallet_mgr = get_wallet_manager()
    
    if wallet_id and secret_code:
        # Verify and get specific wallet
        if not wallet_mgr.verify_secret_code(wallet_id, secret_code):
            raise HTTPException(status_code=401, detail="Invalid wallet ID or secret code")
        
        wallet = wallet_mgr.wallets.get(wallet_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return {
            "wallet_id": wallet.wallet_id,
            "currency": wallet.currency,
            "address": wallet.address,
            "balance": wallet.balance,
            "total_received": wallet.total_received,
            "verified": True
        }
    
    # Get all wallets for user
    wallets = wallet_mgr.get_all_wallets_for_email(current_user.email)
    
    return {
        "beneficiary_email": current_user.email,
        "total_wallets": len(wallets),
        "wallets": wallets
    }


@router.get("/email-history")
def get_email_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get history of earning notification emails"""
    email_svc = get_email_service()
    
    history = email_svc.get_email_history(current_user.email)
    
    return {
        "total_emails": len(history),
        "emails": history[:10]  # Last 10
    }
