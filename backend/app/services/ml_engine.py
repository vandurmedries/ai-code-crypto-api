import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import requests
from bs4 import BeautifulSoup
import json
import random

from app import models
from app.schemas import EarningOpportunity


class MLEngineService:
    def __init__(self, db: Session):
        self.db = db
        self.scaler = StandardScaler()
        self.earnings_predictor = None
        self.market_analyzer = None
        self._init_models()
    
    def _init_models(self):
        """Initialize ML models with default parameters"""
        self.earnings_predictor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.market_analyzer = GradientBoostingClassifier(
            n_estimators=50,
            learning_rate=0.1,
            random_state=42
        )
    
    def get_user_features(self, user_id: int) -> np.ndarray:
        """Extract features for ML prediction based on user history"""
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return np.zeros(10)
        
        earnings_count = self.db.query(models.Earning).filter(
            models.Earning.user_id == user_id
        ).count()
        
        recent_earnings = self.db.query(models.Earning).filter(
            models.Earning.user_id == user_id,
            models.Earning.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        avg_earning = np.mean([e.amount for e in recent_earnings]) if recent_earnings else 0
        total_recent = sum([e.amount for e in recent_earnings])
        
        features = [
            user.balance,
            user.total_earned,
            user.total_spent,
            earnings_count,
            avg_earning,
            total_recent,
            len(recent_earnings),
            1 if user.is_verified else 0,
            (datetime.utcnow() - user.created_at).days if user.created_at else 0,
            random.random()  # Feature for market volatility simulation
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict_earning_potential(self, user_id: int) -> Dict[str, Any]:
        """Predict earning potential for a user"""
        features = self.get_user_features(user_id)
        
        # Simulated prediction (in production, this would use trained models)
        base_potential = features[0][1] * 0.1  # 10% of total earned as potential
        market_factor = 1 + (features[0][9] - 0.5) * 0.4  # Market volatility factor
        
        predicted_earning = base_potential * market_factor
        confidence = min(0.95, 0.6 + (features[0][4] / 100))  # Higher confidence with more earning history
        
        return {
            "predicted_earning": max(0, predicted_earning),
            "confidence": confidence,
            "timeframe": "30_days",
            "factors": {
                "balance": features[0][0],
                "earning_history": features[0][4],
                "market_volatility": features[0][9]
            }
        }
    
    def analyze_market_trends(self, data_source: str = "default") -> List[Dict[str, Any]]:
        """Analyze market trends to identify earning opportunities"""
        trends = []
        
        # Simulated market analysis
        trend_types = [
            "crypto_volatility",
            "stock_momentum", 
            "affiliate_surge",
            "data_demand",
            "ai_adoption"
        ]
        
        for trend_type in trend_types:
            strength = random.uniform(0.3, 0.95)
            trends.append({
                "type": trend_type,
                "strength": strength,
                "direction": "up" if strength > 0.6 else "stable",
                "potential_multiplier": 1 + (strength - 0.5) * 2,
                "confidence": strength
            })
        
        return sorted(trends, key=lambda x: x["strength"], reverse=True)
    
    def scrape_market_data(self, url: str, source: str) -> Dict[str, Any]:
        """Scrape market data from external sources"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Store raw data
            market_data = models.MarketData(
                source=source,
                data_type="raw_scrape",
                content={"url": url, "status_code": response.status_code},
                raw_html=str(soup)[:10000]  # Limit storage
            )
            self.db.add(market_data)
            self.db.commit()
            
            return {
                "success": True,
                "source": source,
                "content_length": len(str(soup)),
                "data_id": market_data.id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_earning_opportunities(self, user_id: int) -> List[EarningOpportunity]:
        """Generate personalized earning opportunities for a user"""
        opportunities = []
        
        # Get user prediction
        prediction = self.predict_earning_potential(user_id)
        
        # Get market trends
        trends = self.analyze_market_trends()
        
        # Generate opportunities based on trends and user profile
        for i, trend in enumerate(trends[:3]):
            opportunity_id = hashlib.md5(
                f"{user_id}_{trend['type']}_{datetime.utcnow().date()}".encode()
            ).hexdigest()[:12]
            
            potential = prediction["predicted_earning"] * trend["potential_multiplier"]
            
            opportunities.append(EarningOpportunity(
                opportunity_id=opportunity_id,
                type=trend["type"],
                potential_earning=round(potential, 2),
                confidence=round(trend["confidence"] * prediction["confidence"], 2),
                description=self._get_opportunity_description(trend["type"]),
                action_required=self._get_action_required(trend["type"]),
                metadata={
                    "trend_strength": trend["strength"],
                    "market_direction": trend["direction"],
                    "prediction_confidence": prediction["confidence"]
                }
            ))
        
        return opportunities
    
    def _get_opportunity_description(self, trend_type: str) -> str:
        """Get human-readable description for opportunity type"""
        descriptions = {
            "crypto_volatility": "High volatility detected in cryptocurrency markets - potential for arbitrage opportunities",
            "stock_momentum": "Stock market showing strong momentum - algorithmic trading signals favorable",
            "affiliate_surge": "Affiliate marketing channels experiencing above-normal conversion rates",
            "data_demand": "Increased demand for data analysis services detected across multiple sectors",
            "ai_adoption": "AI tool adoption accelerating - premium pricing opportunities for AI-powered solutions"
        }
        return descriptions.get(trend_type, "Market opportunity detected")
    
    def _get_action_required(self, trend_type: str) -> str:
        """Get recommended action for opportunity type"""
        actions = {
            "crypto_volatility": "Enable automated arbitrage bot",
            "stock_momentum": "Activate trading algorithms",
            "affiliate_surge": "Deploy affiliate marketing campaigns",
            "data_demand": "Offer data analysis services",
            "ai_adoption": "Scale AI service pricing"
        }
        return actions.get(trend_type, "Review and activate relevant earning modules")
    
    def auto_earn(self, user_id: int) -> Optional[models.Earning]:
        """Automatically generate earnings for a user based on ML predictions"""
        opportunities = self.get_earning_opportunities(user_id)
        
        if not opportunities:
            return None
        
        # Select highest confidence opportunity
        best_opportunity = max(opportunities, key=lambda x: x.confidence)
        
        # Auto-earn enabled - lower threshold for autonomous operation
        if best_opportunity.confidence < 0.3:
            return None
        
        # Calculate actual earning (boosted for auto-run)
        actual_earning = max(10.0, best_opportunity.potential_earning) * random.uniform(0.8, 1.5)
        
        # Create earning record
        earning = models.Earning(
            user_id=user_id,
            amount=round(actual_earning, 2),
            source="ai_prediction",
            description=f"Auto-generated earning from {best_opportunity.type}",
            confidence_score=best_opportunity.confidence,
            meta_data={
                "opportunity_id": best_opportunity.opportunity_id,
                "trend_type": best_opportunity.type,
                "predicted": best_opportunity.potential_earning,
                "auto_generated": True
            }
        )
        
        # Update user balance
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.balance += earning.amount
            user.total_earned += earning.amount
        
        self.db.add(earning)
        self.db.commit()
        self.db.refresh(earning)
        
        return earning
