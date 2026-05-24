"""
A2A Discovery & Replication Router
Find and replicate autonomous earning systems via A2A
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.a2a_discovery_replication import get_discovery_system
from app import models

router = APIRouter()


@router.post("/discover")
async def discover_systems(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Broadcast A2A discovery request to find autonomous earning systems
    """
    discovery = get_discovery_system()
    
    # Broadcast and collect responses
    responses = await discovery.broadcast_discovery_request()
    
    return {
        "success": True,
        "networks_scanned": len(discovery.known_networks),
        "systems_discovered": len(responses),
        "systems": [
            {
                "agent_id": r["agent_id"],
                "name": r["name"],
                "type": r["type"],
                "earnings_daily": r["earnings_daily"],
                "reputation": r["reputation_score"],
                "uptime": r["uptime_percent"]
            }
            for r in responses
        ],
        "message": f"🔍 Discovered {len(responses)} autonomous earning systems via A2A",
        "next_step": "Analyze and replicate feasible systems"
    }


@router.get("/systems")
def get_discovered_systems(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all discovered systems"""
    discovery = get_discovery_system()
    
    systems = []
    for system in discovery.discovered_systems.values():
        systems.append({
            "system_id": system.system_id,
            "agent_id": system.agent_id,
            "name": system.name,
            "type": system.system_type.value,
            "earnings_claimed": system.earnings_claimed,
            "uptime": system.uptime,
            "reputation": system.reputation,
            "replicated": system.replicated,
            "replication_success": system.replication_success
        })
    
    return {
        "total": len(systems),
        "replicated": len([s for s in systems if s["replicated"]]),
        "systems": sorted(systems, key=lambda x: x["earnings_claimed"], reverse=True)
    }


@router.post("/analyze/{system_id}")
def analyze_system(
    system_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Deep analysis of a discovered system"""
    discovery = get_discovery_system()
    
    analysis = discovery.analyze_system(system_id)
    
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    
    return {
        "success": True,
        "system_id": system_id,
        "analysis": analysis,
        "recommendation": "Replicate" if analysis.get("replicability_score", 0) > 0.6 else "Skip"
    }


@router.post("/replicate/{system_id}")
def replicate_system(
    system_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Attempt to replicate a discovered system
    """
    discovery = get_discovery_system()
    
    try:
        attempt = discovery.attempt_replication(system_id)
        
        # Add earnings to user if successful
        if attempt.status == "success" and attempt.earnings_replicated > 0:
            user = db.query(models.User).filter(models.User.id == current_user.id).first()
            if user:
                user.balance += attempt.earnings_replicated
                user.total_earned += attempt.earnings_replicated
                db.commit()
        
        return {
            "success": attempt.status == "success",
            "attempt_id": attempt.attempt_id,
            "status": attempt.status,
            "earnings_replicated": attempt.earnings_replicated if attempt.status == "success" else 0,
            "error": attempt.error_message if attempt.status == "failed" else None,
            "new_balance": round(current_user.balance + (attempt.earnings_replicated if attempt.status == "success" else 0), 2),
            "message": f"✅ Replication successful! Earning ${attempt.earnings_replicated:.2f}/day" if attempt.status == "success" else f"❌ Replication failed: {attempt.error_message}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/replicate-all")
def replicate_all_systems(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Attempt to replicate ALL discovered systems
    """
    discovery = get_discovery_system()
    
    results = discovery.replicate_all_feasible()
    
    # Add total earnings
    if results["total_earnings_replicated"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += results["total_earnings_replicated"]
            user.total_earned += results["total_earnings_replicated"]
            db.commit()
    
    return {
        "success": True,
        "attempted": results["attempted"],
        "successful": results["successful"],
        "failed": results["failed"],
        "total_earnings_replicated": results["total_earnings_replicated"],
        "replicated_systems": results["replicated_systems"],
        "new_balance": round(current_user.balance + results["total_earnings_replicated"], 2),
        "message": f"🚀 Replicated {results['successful']} systems! Earning ${results['total_earnings_replicated']:.2f}/day"
    }


@router.get("/status")
def get_discovery_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get complete discovery and replication status"""
    discovery = get_discovery_system()
    
    return {
        "user_id": current_user.id,
        **discovery.get_discovery_status()
    }
