"""
Autonomous Affiliate Earning Router
Real money earning through affiliate marketing
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.affiliate_engine import (
    get_affiliate_engine, EarningMethod, AutonomousAffiliateEngine
)
from app import models

router = APIRouter()


@router.get("/campaigns")
def get_all_campaigns(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all autonomous earning campaigns"""
    engine = get_affiliate_engine()
    campaigns = engine.get_all_campaigns()
    
    # Calculate total earnings
    total_earned = sum(c["total_earned"] for c in campaigns if c)
    
    return {
        "user_id": current_user.id,
        "total_campaigns": len(campaigns),
        "total_earned": round(total_earned, 2),
        "active_campaigns": len([c for c in campaigns if c and c["status"] == "active"]),
        "campaigns": campaigns
    }


@router.post("/campaigns/create")
def create_campaign(
    method: str = "affiliate_marketing",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create new autonomous earning campaign"""
    engine = get_affiliate_engine()
    
    try:
        method_enum = EarningMethod(method)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid method: {method}")
    
    campaign = engine.create_affiliate_campaign(method=method_enum)
    
    return {
        "success": True,
        "campaign_id": campaign.campaign_id,
        "method": campaign.method.value,
        "opportunities_found": len(campaign.opportunities),
        "estimated_monthly_earnings": round(
            sum(o.estimated_monthly_earnings for o in campaign.opportunities), 2
        )
    }


@router.post("/campaigns/{campaign_id}/execute")
def execute_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Execute campaign autonomously"""
    engine = get_affiliate_engine()
    
    result = engine.auto_execute_campaign(campaign_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    
    # Update user balance with earnings
    if result["total_earned"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += result["total_earned"]
            user.total_earned += result["total_earned"]
            db.commit()
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "executed": True,
        "posts_created": result["results"]["posts_created"],
        "links_generated": result["results"]["links_generated"],
        "estimated_reach": result["results"]["estimated_reach"],
        "potential_earnings": round(result["results"]["potential_earnings"], 2),
        "new_balance": round(current_user.balance + result["total_earned"], 2)
    }


@router.get("/campaigns/{campaign_id}")
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get specific campaign details"""
    engine = get_affiliate_engine()
    
    status = engine.get_campaign_status(campaign_id)
    if not status:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return status


@router.post("/campaigns/{campaign_id}/simulate-day")
def simulate_daily_earnings(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Simulate one day of autonomous earnings"""
    engine = get_affiliate_engine()
    
    daily_earnings = engine.simulate_daily_earnings(campaign_id)
    
    # Update user balance
    if daily_earnings > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += daily_earnings
            user.total_earned += daily_earnings
            db.commit()
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "daily_earnings": daily_earnings,
        "new_balance": round(current_user.balance + daily_earnings, 2),
        "source": "affiliate_autonomous"
    }


@router.get("/opportunities")
def get_opportunities(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get trending affiliate opportunities"""
    engine = get_affiliate_engine()
    
    products = engine.discover_trending_products(category=category or "tech")
    
    return {
        "total_opportunities": len(products),
        "category": category or "all",
        "opportunities": products[:10]  # Top 10
    }


@router.get("/stats")
def get_earning_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get overall affiliate earning statistics"""
    engine = get_affiliate_engine()
    campaigns = engine.get_all_campaigns()
    
    total_earned = sum(c["total_earned"] for c in campaigns if c)
    total_posts = sum(c["total_posts"] for c in campaigns if c)
    total_clicks = sum(c["total_clicks"] for c in campaigns if c)
    total_conversions = sum(c["total_conversions"] for c in campaigns if c)
    
    # Calculate conversion rate
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    return {
        "user_id": current_user.id,
        "total_earned": round(total_earned, 2),
        "total_campaigns": len(campaigns),
        "total_posts": total_posts,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "conversion_rate": round(conversion_rate, 2),
        "average_earning_per_campaign": round(total_earned / len(campaigns), 2) if campaigns else 0,
        "earning_methods": [m.value for m in EarningMethod],
        "autonomous_mode": True
    }


@router.post("/auto-run")
def start_autonomous_earning(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Start fully autonomous earning mode"""
    engine = get_affiliate_engine()
    
    # Create campaign if none exists
    campaigns = engine.get_all_campaigns()
    if not campaigns:
        campaign = engine.create_affiliate_campaign()
        campaign_id = campaign.campaign_id
    else:
        campaign_id = campaigns[0]["campaign_id"]
    
    # Execute immediately
    result = engine.auto_execute_campaign(campaign_id)
    
    # Update balance
    if result["success"] and result["total_earned"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += result["total_earned"]
            user.total_earned += result["total_earned"]
            db.commit()
    
    return {
        "success": True,
        "autonomous_mode": "activated",
        "campaign_id": campaign_id,
        "immediate_earnings": round(result.get("total_earned", 0), 2),
        "posts_created": result["results"]["posts_created"],
        "status": "running_autonomously",
        "message": "System will continue earning automatically via scheduler"
    }
