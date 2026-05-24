from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.ml_engine import MLEngineService
from app.schemas import EarningOpportunity, MarketDataScrape
from app import models

router = APIRouter()


@router.get("/opportunities", response_model=List[EarningOpportunity])
def get_opportunities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get personalized earning opportunities based on ML analysis"""
    ml_service = MLEngineService(db)
    opportunities = ml_service.get_earning_opportunities(current_user.id)
    return opportunities


@router.get("/predict-earnings")
def predict_earnings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get ML prediction for user's earning potential"""
    ml_service = MLEngineService(db)
    prediction = ml_service.predict_earning_potential(current_user.id)
    return prediction


@router.get("/market-trends")
def get_market_trends(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current market trend analysis"""
    ml_service = MLEngineService(db)
    trends = ml_service.analyze_market_trends()
    return {
        "trends": trends,
        "analyzed_at": "2024-01-01T00:00:00",  # Would be actual timestamp
        "source": "AI Market Analyzer"
    }


@router.post("/scrape")
def scrape_data(
    scrape_request: MarketDataScrape,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Scrape market data from external source"""
    ml_service = MLEngineService(db)
    result = ml_service.scrape_market_data(scrape_request.url, scrape_request.source)
    return result


@router.post("/trigger-auto-earn")
def trigger_auto_earn(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Manually trigger auto-earning process (for testing)"""
    target_user_id = user_id if user_id else current_user.id
    
    # Only allow admin users to trigger for other users
    if user_id and user_id != current_user.id:
        # In production, check admin role here
        pass
    
    ml_service = MLEngineService(db)
    earning = ml_service.auto_earn(target_user_id)
    
    if earning:
        return {
            "success": True,
            "earning": {
                "id": earning.id,
                "amount": earning.amount,
                "source": earning.source,
                "confidence": earning.confidence_score,
                "created_at": earning.created_at
            },
            "new_balance": current_user.balance if target_user_id == current_user.id else None
        }
    
    return {
        "success": False,
        "message": "No high-confidence earning opportunities found at this time"
    }


@router.get("/model-stats")
def get_model_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get statistics about ML model performance"""
    models_count = db.query(models.MLModel).filter(
        models.MLModel.is_active == True
    ).count()
    
    predictions_count = db.query(models.MLPrediction).count()
    
    accurate_predictions = db.query(models.MLPrediction).filter(
        models.MLPrediction.was_correct == True
    ).count()
    
    accuracy = accurate_predictions / predictions_count if predictions_count > 0 else 0
    
    return {
        "active_models": models_count,
        "total_predictions": predictions_count,
        "accuracy_rate": round(accuracy, 3),
        "avg_confidence": 0.82  # Simulated
    }
