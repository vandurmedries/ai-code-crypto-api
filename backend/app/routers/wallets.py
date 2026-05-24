from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import hashlib
import os

from app.database import get_db
from app.services.auth import get_current_active_user
from app import models
from app.schemas import WalletCreate, Wallet, WalletTransaction

router = APIRouter()


@router.get("/", response_model=List[Wallet])
def get_wallets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all wallets for current user"""
    wallets = db.query(models.Wallet).filter(
        models.Wallet.user_id == current_user.id,
        models.Wallet.is_active == True
    ).all()
    return wallets


@router.post("/create")
def create_wallet(
    currency: str,
    network: str = "mainnet",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new wallet for a cryptocurrency"""
    
    # Check if wallet already exists
    existing = db.query(models.Wallet).filter(
        models.Wallet.user_id == current_user.id,
        models.Wallet.currency == currency,
        models.Wallet.network == network
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Wallet for {currency} already exists")
    
    # Generate a unique address (in production, use actual crypto libraries)
    unique_string = f"{current_user.id}_{currency}_{network}_{os.urandom(16).hex()}"
    address = hashlib.sha256(unique_string.encode()).hexdigest()[:34]
    
    # Create wallet
    wallet = models.Wallet(
        user_id=current_user.id,
        currency=currency,
        network=network,
        address=address,
        wallet_type="platform",
        balance=0.0,
        pending_balance=0.0
    )
    
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    
    return {
        "message": f"Wallet created for {currency}",
        "wallet": {
            "id": wallet.id,
            "currency": wallet.currency,
            "address": wallet.address,
            "balance": wallet.balance
        }
    }


@router.get("/{wallet_id}/deposit-address")
def get_deposit_address(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get deposit address for a wallet"""
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return {
        "currency": wallet.currency,
        "network": wallet.network,
        "address": wallet.address,
        "qr_code_url": f"/api/wallets/{wallet_id}/qr"
    }


@router.post("/{wallet_id}/withdraw")
def withdraw(
    wallet_id: int,
    to_address: str,
    amount: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Withdraw funds to an external address"""
    
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create withdrawal transaction
    tx = models.WalletTransaction(
        wallet_id=wallet_id,
        user_id=current_user.id,
        tx_type="withdrawal",
        amount=amount,
        currency=wallet.currency,
        to_address=to_address,
        status="pending"
    )
    
    # Deduct from balance
    wallet.balance -= amount
    
    db.add(tx)
    db.commit()
    
    return {
        "message": f"Withdrawal of {amount} {wallet.currency} initiated",
        "transaction_id": tx.id,
        "status": "pending",
        "to_address": to_address
    }


@router.get("/{wallet_id}/transactions")
def get_transactions(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get transaction history for a wallet"""
    
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    transactions = db.query(models.WalletTransaction).filter(
        models.WalletTransaction.wallet_id == wallet_id
    ).order_by(models.WalletTransaction.created_at.desc()).all()
    
    return {
        "currency": wallet.currency,
        "address": wallet.address,
        "balance": wallet.balance,
        "transactions": [
            {
                "id": tx.id,
                "type": tx.tx_type,
                "amount": tx.amount,
                "status": tx.status,
                "tx_hash": tx.tx_hash,
                "from": tx.from_address,
                "to": tx.to_address,
                "created_at": tx.created_at,
                "confirmed_at": tx.confirmed_at
            }
            for tx in transactions
        ]
    }


@router.post("/simulate-deposit")
def simulate_deposit(
    wallet_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Simulate a deposit (for testing - in production, this would be detected by blockchain monitoring)"""
    
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Create deposit transaction
    tx_hash = hashlib.sha256(f"{wallet_id}_{amount}_{os.urandom(8).hex()}".encode()).hexdigest()[:16]
    
    tx = models.WalletTransaction(
        wallet_id=wallet_id,
        user_id=current_user.id,
        tx_type="deposit",
        amount=amount,
        currency=wallet.currency,
        to_address=wallet.address,
        tx_hash=tx_hash,
        status="confirmed",
        confirmations=6
    )
    
    # Add to balance
    wallet.balance += amount
    
    db.add(tx)
    db.commit()
    
    return {
        "message": f"Deposit of {amount} {wallet.currency} confirmed",
        "transaction_hash": tx_hash,
        "new_balance": wallet.balance
    }
