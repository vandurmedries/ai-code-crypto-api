"""
Passive Income Aggregator Router
Manages 20+ fully automated income streams
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.passive_income_aggregator import get_passive_income_aggregator
from app import models

router = APIRouter()


@router.post("/activate-all")
def activate_all_streams(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Activate all 20 income streams
    """
    service = get_passive_income_aggregator()
    
    result = service.activate_all_streams()
    
    return {
        "user_id": current_user.id,
        **result,
        "message": f"🚀 Activated {result['streams_activated']} income streams",
        "automation_level": "FULLY AUTONOMOUS",
        "human_intervention": "Setup only, then 0 minutes per day"
    }


@router.post("/run-daily")
def run_daily_automation(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run complete daily automation for all active streams
    """
    service = get_passive_income_aggregator()
    
    run = service.run_daily_automation()
    
    # Add to user balance
    if run.total_earned_eur > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += run.total_earned_eur
            user.total_earned += run.total_earned_eur
            db.commit()
    
    return {
        "success": True,
        "run_id": run.run_id,
        "date": run.date,
        "streams_run": run.streams_run,
        "successful": run.successful,
        "failed": run.failed,
        "earned_today_eur": round(run.total_earned_eur, 2),
        "time_saved_minutes": run.time_saved_minutes,
        "issues": run.issues,
        "new_balance": round(current_user.balance + run.total_earned_eur, 2),
        "message": f"🤖 Daily automation: €{run.total_earned_eur:.2f} earned, {run.time_saved_minutes} minutes saved"
    }


@router.get("/stats")
def get_aggregator_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get complete aggregator statistics
    """
    service = get_passive_income_aggregator()
    
    stats = service.get_aggregator_stats()
    
    return {
        "user_id": current_user.id,
        **stats,
        "system_status": "FULLY AUTONOMOUS",
        "human_work_required": "0 minutes daily after setup",
        "monthly_check": "5 minutes to verify earnings"
    }


@router.get("/history")
def get_run_history(
    limit: int = 7,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get recent daily run history
    """
    service = get_passive_income_aggregator()
    
    history = service.get_daily_run_history(limit=limit)
    
    total_earned = sum(r["earned_eur"] for r in history)
    
    return {
        "last_7_days": history,
        "total_earned_7_days": round(total_earned, 2),
        "average_per_day": round(total_earned / len(history), 2) if history else 0,
        "projected_monthly": round(total_earned / len(history) * 30, 2) if history else 0
    }


@router.post("/setup-complete")
def setup_complete_system(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Complete system setup:
    1. Activate all streams
    2. Run first automation
    3. Return full stats
    """
    service = get_passive_income_aggregator()
    
    # Activate
    activation = service.activate_all_streams()
    
    # Run first automation
    first_run = service.run_daily_automation()
    
    if first_run.total_earned_eur > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += first_run.total_earned_eur
            user.total_earned += first_run.total_earned_eur
            db.commit()
    
    return {
        "success": True,
        "setup_complete": True,
        "streams": activation["streams_activated"],
        "setup_time": activation["setup_time_hours"],
        "monthly_potential": activation["monthly_potential"],
        "first_run_earnings": round(first_run.total_earned_eur, 2),
        "status": "FULLY AUTONOMOUS",
        "daily_command": "POST /api/passive-income/run-daily",
        "next_cashout": "Run for 30 days, then withdraw all",
        "message": f"🎉 System ready! {activation['streams_activated']} streams earning automatically."
    }
