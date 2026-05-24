from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import User, UserUpdate, DashboardStats, Earning, Purchase
from app.services.auth import get_current_active_user
from app import models

router = APIRouter()


@router.get("/me", response_model=User)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=User)
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    recent_earnings = db.query(models.Earning).filter(
        models.Earning.user_id == current_user.id
    ).order_by(models.Earning.created_at.desc()).limit(5).all()
    
    recent_purchases = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id
    ).order_by(models.Purchase.created_at.desc()).limit(5).all()
    
    from app.services.ml_engine import MLEngineService
    ml_service = MLEngineService(db)
    opportunities = ml_service.get_earning_opportunities(current_user.id)
    
    return DashboardStats(
        balance=current_user.balance,
        total_earned=current_user.total_earned,
        total_spent=current_user.total_spent,
        recent_earnings=recent_earnings,
        recent_purchases=recent_purchases,
        active_opportunities=opportunities
    )
