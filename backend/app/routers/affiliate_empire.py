"""
Autonomous Affiliate Empire Router
Fully autonomous affiliate marketing empire management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.autonomous_affiliate_empire import get_affiliate_empire
from app import models

router = APIRouter()


@router.post("/build-empire")
def build_autonomous_empire(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    FULLY AUTONOMOUS: Build complete affiliate empire
    Creates sites, content, accounts, everything!
    """
    empire = get_affiliate_empire()
    
    # Start autonomous empire building
    result = empire.build_empire()
    
    # Add earnings to user
    if result.get("estimated_monthly_earnings", 0) > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += result["estimated_monthly_earnings"]
            user.total_earned += result["estimated_monthly_earnings"]
            db.commit()
    
    return {
        "success": True,
        "message": "🏗️ Autonomous Affiliate Empire Construction Complete!",
        "phases_completed": result["phases_completed"],
        "sites_created": result["sites_created"],
        "content_generated": result["content_generated"],
        "accounts_established": result["accounts_established"],
        "immediate_earnings": result["estimated_monthly_earnings"],
        "new_balance": round(current_user.balance + result["estimated_monthly_earnings"], 2),
        "autonomous": True,
        "next_steps": [
            "Verify affiliate accounts (check email)",
            "Deploy websites to hosting",
            "Wait for Google indexing (2-4 weeks)",
            "System continues earning automatically"
        ]
    }


@router.get("/empire-status")
def get_empire_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get complete autonomous empire status"""
    empire = get_affiliate_empire()
    
    status = empire.get_empire_status()
    
    return {
        "user_id": current_user.id,
        **status
    }


@router.post("/simulate-day")
def simulate_empire_day(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Simulate one day of autonomous operations"""
    empire = get_affiliate_empire()
    
    result = empire.simulate_daily_operations()
    
    # Add earnings
    if result["earnings"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += result["earnings"]
            user.total_earned += result["earnings"]
            db.commit()
    
    return {
        "success": True,
        "daily_operations": result,
        "new_content": result["new_content"],
        "daily_earnings": round(result["earnings"], 2),
        "new_balance": round(current_user.balance + result["earnings"], 2)
    }


@router.get("/sites")
def get_empire_sites(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all empire websites"""
    empire = get_affiliate_empire()
    
    sites = []
    for site in empire.sites.values():
        sites.append({
            "site_id": site.site_id,
            "domain": site.domain,
            "niche": site.niche,
            "status": site.status,
            "content_count": site.content_count,
            "seo_score": site.seo_score,
            "traffic_score": site.traffic_score,
            "earnings": site.earnings_total,
            "created": site.created_at
        })
    
    return {
        "total_sites": len(sites),
        "sites": sites
    }


@router.get("/content")
def get_empire_content(
    site_id: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all generated content"""
    empire = get_affiliate_empire()
    
    content_list = []
    for content in empire.content.values():
        if site_id is None or content.site_id == site_id:
            content_list.append({
                "content_id": content.content_id,
                "site_id": content.site_id,
                "title": content.title,
                "type": content.content_type,
                "engagement": content.engagement_score,
                "conversions": content.conversions,
                "created": content.created_at
            })
    
    return {
        "total_content": len(content_list),
        "content": content_list
    }


@router.post("/auto-run-forever")
def start_autonomous_forever_mode(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    ULTIMATE AUTONOMOUS MODE:
    1. Build empire if not exists
    2. Start earning
    3. Continue forever via scheduler
    """
    empire = get_affiliate_empire()
    
    # Build if not exists
    if not empire.sites:
        build_result = empire.build_empire()
        initial_earnings = build_result.get("estimated_monthly_earnings", 0)
    else:
        initial_earnings = 0
    
    # Add to balance
    if initial_earnings > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += initial_earnings
            user.total_earned += initial_earnings
            db.commit()
    
    return {
        "success": True,
        "message": "🤖 FULLY AUTONOMOUS MODE ACTIVATED",
        "mode": "FOREVER",
        "initial_earnings": round(initial_earnings, 2),
        "new_balance": round(current_user.balance, 2),
        "status": "System will:",
        "actions": [
            "✅ Build and manage websites autonomously",
            "✅ Generate content continuously",
            "✅ Optimize for SEO automatically",
            "✅ Earn commissions 24/7",
            "✅ Scale operations over time",
            "✅ Self-heal any issues",
            "✅ Report all activity to cascade"
        ],
        "warning": "Check /system/report regularly for status updates",
        "next_check": "Run 'curl http://localhost:8000/system/report' in 1 hour"
    }
