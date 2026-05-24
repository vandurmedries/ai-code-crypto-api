"""
Crypto Recovery Router
Helps recover lost/forgotten crypto - LEGAL service
Takes 20% fee from successful recoveries only
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.crypto_recovery_service import get_recovery_service, RecoveryType
from app import models

router = APIRouter()


@router.post("/submit-request")
def submit_recovery_request(
    client_email: str = Body(...),
    wallet_type: str = Body(...),  # BTC, ETH, etc.
    recovery_type: str = Body(...),  # forgotten_password, partial_seed, etc.
    wallet_address: str = Body(None),
    partial_info: Dict = Body({}),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Submit a crypto recovery request
    Client provides whatever they remember about lost wallet
    """
    service = get_recovery_service()
    
    # Map string to enum
    type_map = {
        "forgotten_password": RecoveryType.FORGOTTEN_PASSWORD,
        "partial_seed": RecoveryType.PARTIAL_SEED,
        "corrupt_wallet": RecoveryType.CORRUPT_WALLET,
        "old_hardware": RecoveryType.OLD_HARDWARE,
        "unknown": RecoveryType.UNKNOWN
    }
    
    rec_type = type_map.get(recovery_type, RecoveryType.UNKNOWN)
    
    # Create job
    job = service.submit_recovery_request(
        client_email=client_email,
        wallet_type=wallet_type,
        recovery_type=rec_type,
        wallet_address=wallet_address,
        partial_info=partial_info
    )
    
    # Analyze feasibility
    analysis = service.analyze_recovery_feasibility(job.job_id)
    
    return {
        "success": True,
        "job_id": job.job_id,
        "status": "submitted",
        "analysis": analysis,
        "message": "Recovery request submitted for analysis",
        "next_step": "We will analyze feasibility within 24 hours",
        "fee_structure": {
            "success_fee": "20% of recovered funds",
            "no_recovery": "€0 - no fee",
            "analysis": "Free"
        }
    }


@router.post("/attempt-recovery/{job_id}")
def attempt_recovery(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Attempt to recover the lost crypto
    This runs the actual recovery algorithms
    """
    service = get_recovery_service()
    
    result = service.attempt_recovery(job_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    # If successful, add fee to our earnings
    if result.get("success") and result.get("our_fee", 0) > 0:
        fee_amount = result["our_fee"]
        
        # Convert to USD (approximate)
        if result.get("currency") == "BTC":
            usd_fee = fee_amount * 65000
        elif result.get("currency") == "ETH":
            usd_fee = fee_amount * 3500
        else:
            usd_fee = fee_amount
        
        # Add to system user balance
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += usd_fee
            user.total_earned += usd_fee
            db.commit()
        
        result["fee_in_usd"] = round(usd_fee, 2)
        result["added_to_balance"] = round(usd_fee, 2)
    
    return result


@router.get("/service-stats")
def get_recovery_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get recovery service statistics and earnings"""
    service = get_recovery_service()
    
    stats = service.get_service_stats()
    
    return {
        "user_id": current_user.id,
        **stats,
        "business_model": "Crypto Recovery as a Service",
        "legality": "100% Legal - We help recover OWN lost funds only",
        "pricing": "20% success fee only"
    }


@router.get("/pending-jobs")
def get_pending_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all pending recovery jobs"""
    service = get_recovery_service()
    
    pending = service.list_pending_jobs()
    
    return {
        "total_pending": len(pending),
        "jobs": pending,
        "potential_revenue": f"€{len(pending) * 0.15 * 5000:.0f} estimated"  # 15% success * avg recovery
    }


@router.post("/simulate-incoming-request")
def simulate_incoming_request(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Simulate an incoming recovery request
    For testing/demonstration purposes
    """
    service = get_recovery_service()
    
    # Simulate random request
    import random
    
    wallet_types = ["BTC", "ETH", "LTC", "DOGE"]
    recovery_types = ["forgotten_password", "partial_seed", "corrupt_wallet"]
    
    job = service.submit_recovery_request(
        client_email=f"client{random.randint(100,999)}@gmail.com",
        wallet_type=random.choice(wallet_types),
        recovery_type=RecoveryType(random.choice(recovery_types)),
        wallet_address=f"0x{random.randint(100000000000,999999999999)}",
        partial_info={
            "password_hints": ["dog", "birthday", "1990"],
            "known_characters": "Pa$$",
            "wallet_created_year": 2019
        }
    )
    
    return {
        "success": True,
        "simulated": True,
        "job_id": job.job_id,
        "message": f"Simulated recovery request: {job.wallet_type} wallet",
        "analysis": service.analyze_recovery_feasibility(job.job_id)
    }


@router.post("/run-batch-recovery")
def run_batch_recovery(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run batch recovery on all pending jobs
    Processes multiple recovery attempts
    """
    service = get_recovery_service()
    
    pending = service.list_pending_jobs()
    
    results = {
        "attempted": 0,
        "successful": 0,
        "failed": 0,
        "total_fees_earned_crypto": 0.0,
        "total_fees_earned_usd": 0.0,
        "details": []
    }
    
    for job_info in pending[:5]:  # Process max 5 at a time
        job_id = job_info["job_id"]
        
        result = service.attempt_recovery(job_id)
        results["attempted"] += 1
        
        if result.get("success"):
            results["successful"] += 1
            results["total_fees_earned_crypto"] += result.get("our_fee", 0)
            results["total_fees_earned_usd"] += result.get("fee_in_usd", 0)
        else:
            results["failed"] += 1
        
        results["details"].append({
            "job_id": job_id,
            "success": result.get("success"),
            "recovered": result.get("recovered_amount"),
            "fee": result.get("our_fee")
        })
    
    # Add to balance
    if results["total_fees_earned_usd"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += results["total_fees_earned_usd"]
            user.total_earned += results["total_fees_earned_usd"]
            db.commit()
    
    return {
        "success": True,
        **results,
        "new_balance": round(current_user.balance + results["total_fees_earned_usd"], 2),
        "message": f"Batch complete: {results['successful']}/{results['attempted']} successful"
    }
