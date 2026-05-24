from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.schemas import Earning, EarningCreate
from app.services.auth import get_current_active_user
from app import models

router = APIRouter()


@router.get("/", response_model=List[Earning])
def get_earnings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    earnings = db.query(models.Earning).filter(
        models.Earning.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return earnings


@router.get("/total")
def get_total_earnings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    total = db.query(models.Earning).filter(
        models.Earning.user_id == current_user.id
    ).count()
    
    total_amount = db.query(models.Earning).filter(
        models.Earning.user_id == current_user.id
    ).with_entities(models.Earning.amount).all()
    
    total_sum = sum(e[0] for e in total_amount) if total_amount else 0
    
    return {
        "total_count": total,
        "total_amount": total_sum,
        "by_source": get_earnings_by_source(db, current_user.id)
    }


def get_earnings_by_source(db: Session, user_id: int):
    sources = ['ai_prediction', 'affiliate', 'data_analysis', 'market_trend']
    result = {}
    for source in sources:
        amount = db.query(models.Earning).filter(
            models.Earning.user_id == user_id,
            models.Earning.source == source
        ).with_entities(models.Earning.amount).all()
        result[source] = sum(e[0] for e in amount) if amount else 0
    return result


@router.post("/credit")
def credit_earning(
    amount: float,
    source: str,
    description: str = None,
    confidence_score: float = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    earning = models.Earning(
        user_id=current_user.id,
        amount=amount,
        source=source,
        description=description,
        confidence_score=confidence_score
    )
    db.add(earning)
    
    current_user.balance += amount
    current_user.total_earned += amount
    
    db.commit()
    db.refresh(earning)
    
    return {
        "message": f"Credited {amount} to account",
        "earning": earning,
        "new_balance": current_user.balance
    }
