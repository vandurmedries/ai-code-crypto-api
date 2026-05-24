"""
Rewards Aggregator Router
API endpoints for automated reward points collection
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.rewards_aggregator import get_rewards_aggregator, RewardPlatform
from app import models

router = APIRouter()


@router.post("/create-account")
def create_reward_account(
    platform: str = Body(...),  # microsoft_rewards, swagbucks, etc.
    email: str = Body(...),
    account_count: int = Body(1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create reward accounts for a platform
    """
    service = get_rewards_aggregator()
    
    # Map string to enum
    platform_map = {
        "microsoft_rewards": RewardPlatform.MICROSOFT_REWARDS,
        "swagbucks": RewardPlatform.SWAGBUCKS,
        "fetch": RewardPlatform.FETCH_REWARDS,
        "google_opinion": RewardPlatform.GOOGLE_OPINION,
        "mistplay": RewardPlatform.MISTPLAY
    }
    
    platform_enum = platform_map.get(platform)
    if not platform_enum:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    accounts = service.create_reward_account(
        platform=platform_enum,
        email=email,
        account_count=account_count
    )
    
    return {
        "success": True,
        "accounts_created": len(accounts),
        "accounts": [
            {
                "account_id": a.account_id,
                "platform": a.platform.value,
                "email": a.email,
                "daily_target": a.daily_points_target
            }
            for a in accounts
        ],
        "warning": "⚠️ Multiple accounts may violate platform ToS"
    }


@router.post("/run-daily/{account_id}")
def run_daily_automation(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run daily automation for a specific account
    """
    service = get_rewards_aggregator()
    
    result = service.simulate_daily_automation(account_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Add to balance if successful
    if result.get("success") and result.get("eur_value_today", 0) > 0:
        eur_earned = result["eur_value_today"]
        
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += eur_earned
            user.total_earned += eur_earned
            db.commit()
    
    return {
        "success": True,
        **result,
        "message": f"💰 Earned {result.get('points_earned_today', 0)} points (€{result.get('eur_value_today', 0)})",
        "added_to_balance": result.get("eur_value_today", 0)
    }


@router.post("/run-all-daily")
def run_all_daily(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run daily automation for ALL accounts
    """
    service = get_rewards_aggregator()
    
    results = service.run_all_accounts_daily()
    
    # Add to balance
    if results.get("total_eur_today", 0) > 0:
        total_eur = results["total_eur_today"]
        
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += total_eur
            user.total_earned += total_eur
            db.commit()
    
    return {
        "success": True,
        **results,
        "new_balance": round(current_user.balance + results.get("total_eur_today", 0), 2),
        "message": f"🤖 Daily run complete! €{results.get('total_eur_today', 0)} from {results.get('active_accounts', 0)} accounts"
    }


@router.get("/stats")
def get_aggregator_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get complete aggregator statistics"""
    service = get_rewards_aggregator()
    
    stats = service.get_aggregator_stats()
    
    return {
        "user_id": current_user.id,
        **stats,
        "business_model": "Automated Reward Points Collection",
        "legal_note": "Grijs gebied - kan account bans veroorzaken",
        "recommendation": "Gebruik VPN, roteer accounts, verwacht bans"
    }


@router.post("/setup-farm")
def setup_complete_farm(
    base_email: str = Body(...),
    microsoft_count: int = Body(5),
    fetch_count: int = Body(3),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Setup complete reward farm with multiple accounts
    """
    service = get_rewards_aggregator()
    
    created = []
    
    # Create Microsoft accounts
    if microsoft_count > 0:
        ms_accounts = service.create_reward_account(
            RewardPlatform.MICROSOFT_REWARDS,
            base_email,
            microsoft_count
        )
        created.extend([{"platform": "microsoft", "id": a.account_id} for a in ms_accounts])
    
    # Create Fetch accounts
    if fetch_count > 0:
        fetch_accounts = service.create_reward_account(
            RewardPlatform.FETCH_REWARDS,
            base_email,
            fetch_count
        )
        created.extend([{"platform": "fetch", "id": a.account_id} for a in fetch_accounts])
    
    return {
        "success": True,
        "total_accounts": len(created),
        "accounts": created,
        "setup_complete": True,
        "next_steps": [
            "1. Create real accounts on each platform",
            "2. Use unique phone numbers for verification",
            "3. Setup VPN rotation (different IP per account)",
            "4. Run /run-all-daily daily",
            "5. Cash out monthly to PayPal/gift cards"
        ],
        "expected_monthly": f"€{len(created) * 2} - €{len(created) * 8}",
        "risks": "Account bans: 5-10% per maand per account"
    }
