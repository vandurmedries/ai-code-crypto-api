"""
Prompt Marketplace Router
API endpoints for prompt goldmine system
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.prompt_marketplace import get_prompt_marketplace
from app import models

router = APIRouter()


@router.post("/discover")
def discover_prompts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Discover valuable prompts from various sources
    Scans for high-quality, monetizable prompts
    """
    marketplace = get_prompt_marketplace()
    
    discoveries = marketplace.discover_valuable_prompts(source="autonomous_scanner")
    
    return {
        "success": True,
        "discovered": len(discoveries),
        "discoveries": [
            {
                "id": d.discovery_id,
                "category": d.category.value,
                "estimated_value": d.estimated_value,
                "source": d.source
            }
            for d in discoveries
        ],
        "message": f"💎 Discovered {len(discoveries)} high-value prompts"
    }


@router.post("/curate/{discovery_id}")
def curate_prompt(
    discovery_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Turn discovered prompt into marketplace listing
    """
    marketplace = get_prompt_marketplace()
    
    prompt = marketplace.curate_prompt_for_sale(discovery_id)
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Discovery not found")
    
    return {
        "success": True,
        "prompt_id": prompt.prompt_id,
        "title": prompt.title,
        "category": prompt.category.value,
        "price": prompt.price,
        "quality_score": prompt.quality_score,
        "status": "listed_for_sale",
        "message": f"✅ Prompt curated and listed: €{prompt.price}"
    }


@router.post("/simulate-sale/{prompt_id}")
def simulate_prompt_sale(
    prompt_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Simulate a prompt sale (for testing/demo)
    """
    marketplace = get_prompt_marketplace()
    
    result = marketplace.simulate_sale(prompt_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    # Add commission to system balance
    if result.get("platform_commission", 0) > 0:
        commission = result["platform_commission"]
        
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += commission
            user.total_earned += commission
            db.commit()
    
    return {
        "success": True,
        **result,
        "new_balance": round(current_user.balance + result.get("platform_commission", 0), 2),
        "message": f"💰 Prompt sold! Earned €{result.get('platform_commission', 0)} commission"
    }


@router.post("/batch-sales")
def run_batch_sales(
    count: int = Body(10),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Simulate batch sales for revenue generation
    """
    marketplace = get_prompt_marketplace()
    
    result = marketplace.batch_simulate_sales(count=count)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Add commission to balance
    if result.get("total_commission", 0) > 0:
        total_commission = result["total_commission"]
        
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += total_commission
            user.total_earned += total_commission
            db.commit()
    
    return {
        "success": True,
        **result,
        "new_balance": round(current_user.balance + result.get("total_commission", 0), 2),
        "message": f"🚀 Batch complete! Earned €{result.get('total_commission', 0)} from {count} sales"
    }


@router.get("/marketplace-stats")
def get_marketplace_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get complete marketplace statistics"""
    marketplace = get_prompt_marketplace()
    
    stats = marketplace.get_marketplace_stats()
    
    return {
        "user_id": current_user.id,
        **stats,
        "business_model": "Prompt Marketplace - 20% commission",
        "autonomous": True
    }


@router.get("/top-prompts")
def get_top_prompts(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get top performing prompts"""
    marketplace = get_prompt_marketplace()
    
    top_prompts = marketplace.get_top_performing_prompts(limit=limit)
    
    return {
        "top_prompts": top_prompts,
        "total_count": len(marketplace.prompts)
    }


@router.post("/autonomous-run")
def run_autonomous_marketplace(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Full autonomous marketplace cycle:
    1. Discover prompts
    2. Curate them
    3. Simulate sales
    4. Generate revenue
    """
    marketplace = get_prompt_marketplace()
    
    # Step 1: Discover
    discoveries = marketplace.discover_valuable_prompts()
    
    # Step 2: Curate all discovered
    curated = []
    for disc in discoveries:
        prompt = marketplace.curate_prompt_for_sale(disc.discovery_id)
        if prompt:
            curated.append(prompt)
    
    # Step 3: Batch sales
    if curated:
        sales_result = marketplace.batch_simulate_sales(count=len(curated) * 3)  # 3x sales per prompt
        
        # Add to balance
        if sales_result.get("total_commission", 0) > 0:
            total_commission = sales_result["total_commission"]
            
            user = db.query(models.User).filter(models.User.id == current_user.id).first()
            if user:
                user.balance += total_commission
                user.total_earned += total_commission
                db.commit()
        
        return {
            "success": True,
            "discovered": len(discoveries),
            "curated": len(curated),
            "sales": sales_result,
            "new_balance": round(current_user.balance + sales_result.get("total_commission", 0), 2),
            "message": f"🤖 Autonomous marketplace complete! Discovered {len(discoveries)} prompts, earned €{sales_result.get('total_commission', 0)}"
        }
    
    return {
        "success": False,
        "message": "No prompts discovered to curate"
    }
