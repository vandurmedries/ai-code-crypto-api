from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import stripe
import os

from app.database import get_db
from app.schemas import Purchase, PurchaseCreate
from app.services.auth import get_current_active_user
from app import models

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key_here")

PRODUCTS = {
    "ai_bot_basic": {"name": "AI Bot - Basic", "price": 29.99},
    "ai_bot_pro": {"name": "AI Bot - Professional", "price": 99.99},
    "ai_bot_enterprise": {"name": "AI Bot - Enterprise", "price": 299.99},
    "market_analyzer": {"name": "Market Analyzer", "price": 49.99},
    "data_scraper": {"name": "Data Scraper Pro", "price": 39.99},
    "prediction_api": {"name": "Prediction API Access", "price": 199.99},
}


@router.get("/products")
def get_products():
    return PRODUCTS


@router.get("/", response_model=List[Purchase])
def get_purchases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    purchases = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return purchases


@router.post("/create")
def create_purchase(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = PRODUCTS[product_id]
    
    if current_user.balance < product["price"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient balance. Required: ${product['price']}, Available: ${current_user.balance}"
        )
    
    purchase = models.Purchase(
        user_id=current_user.id,
        product_id=product_id,
        product_name=product["name"],
        amount=product["price"],
        status="completed"
    )
    
    current_user.balance -= product["price"]
    current_user.total_spent += product["price"]
    
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    return {
        "message": f"Successfully purchased {product['name']}",
        "purchase": purchase,
        "new_balance": current_user.balance
    }


@router.post("/stripe-intent")
def create_stripe_intent(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = PRODUCTS[product_id]
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(product["price"] * 100),  # Convert to cents
            currency="usd",
            metadata={
                "user_id": current_user.id,
                "product_id": product_id,
                "product_name": product["name"]
            }
        )
        
        return {
            "client_secret": intent.client_secret,
            "amount": product["price"]
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm-stripe")
def confirm_stripe_purchase(
    payment_intent_id: str,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = PRODUCTS[product_id]
    
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != "succeeded":
            raise HTTPException(status_code=400, detail="Payment not successful")
        
        purchase = models.Purchase(
            user_id=current_user.id,
            product_id=product_id,
            product_name=product["name"],
            amount=product["price"],
            status="completed",
            stripe_payment_id=payment_intent_id
        )
        
        current_user.total_spent += product["price"]
        
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        
        return {
            "message": f"Successfully purchased {product['name']}",
            "purchase": purchase
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
