"""
Self-Configuring A2A Earner Router
Autonomous system that discovers, configures, and earns
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.self_configuring_a2a_earner import get_self_earner
from app import models

router = APIRouter()


@router.post("/autonomous-setup")
async def run_autonomous_setup(
    beneficiary_email: str = Body("user@example.com"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    FULLY AUTONOMOUS SETUP:
    1. Discovers earning strategies via A2A
    2. Learns configuration from other agents
    3. Self-configures
    4. Sets user as beneficiary
    5. Starts earning
    """
    earner = get_self_earner(beneficiary_email)
    
    try:
        result = await earner.run_full_setup(beneficiary_email)
        
        # Add earnings to user if successful
        if result["earning"]["daily_earnings"] > 0:
            user = db.query(models.User).filter(models.User.id == current_user.id).first()
            if user:
                user.balance += result["earning"]["daily_earnings"]
                user.total_earned += result["earning"]["daily_earnings"]
                db.commit()
        
        return {
            "success": True,
            "user_id": current_user.id,
            **result,
            "new_balance": round(current_user.balance + result["earning"]["daily_earnings"], 2),
            "message": "🤖 AUTONOMOUS SYSTEM ACTIVE! Earning money via A2A network..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover-strategies")
async def discover_strategies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Discover earning strategies via A2A"""
    earner = get_self_earner(current_user.email)
    
    strategies = await earner.discover_earning_strategies()
    
    return {
        "success": True,
        "strategies_found": len(strategies),
        "strategies": [
            {
                "id": s.strategy_id,
                "name": s.name,
                "description": s.description,
                "complexity": s.setup_complexity,
                "earning_potential": s.earning_potential,
                "risk": s.risk_level,
                "a2a_endpoint": s.a2a_endpoint
            }
            for s in strategies
        ],
        "recommended": min(strategies, key=lambda s: s.setup_complexity / s.earning_potential).name if strategies else None
    }


@router.post("/configure/{strategy_id}")
async def configure_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Self-configure selected strategy"""
    earner = get_self_earner(current_user.email)
    
    try:
        config = await earner.self_configure(strategy_id)
        
        return {
            "success": True,
            "configuration_id": config.config_id,
            "strategy_id": strategy_id,
            "status": config.status.value,
            "steps_completed": len(config.steps_completed),
            "beneficiary": config.beneficiary.email if config.beneficiary else None,
            "message": "✅ System self-configured via A2A!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-earning")
async def start_earning(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Start autonomous earning"""
    earner = get_self_earner(current_user.email)
    
    try:
        result = await earner.start_autonomous_earning()
        
        # Add to user balance
        if result["daily_earnings"] > 0:
            user = db.query(models.User).filter(models.User.id == current_user.id).first()
            if user:
                user.balance += result["daily_earnings"]
                user.total_earned += result["daily_earnings"]
                db.commit()
        
        return {
            "success": True,
            **result,
            "new_balance": round(current_user.balance + result["daily_earnings"], 2),
            "message": f"💰 Autonomous earning active! ${result['daily_earnings']:.2f}/day → {result['beneficiary']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def get_self_earning_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get autonomous earner status"""
    earner = get_self_earner(current_user.email)
    
    status = earner.get_status()
    
    return {
        "user_id": current_user.id,
        **status,
        "autonomous_mode": True,
        "a2a_enabled": True,
        "mcp_enabled": True
    }
