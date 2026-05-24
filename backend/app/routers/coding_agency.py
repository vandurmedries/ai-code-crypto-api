"""
Coding Agency Router
Earn money by coding with A2A and MCP
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.autonomous_coding_agency import get_coding_agency, ServiceType
from app import models

router = APIRouter()


@router.get("/status")
def get_coding_agency_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get coding agency status and earnings"""
    agency = get_coding_agency()
    
    return {
        "user_id": current_user.id,
        **agency.get_agency_status()
    }


@router.post("/work-cycle")
def run_work_cycle(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run one work cycle:
    1. Find coding jobs via A2A
    2. Match with agents
    3. Complete work
    4. Earn money
    """
    agency = get_coding_agency()
    
    result = agency.simulate_work_cycle()
    
    # Add earnings to user
    if result["cycle_earnings"] > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += result["cycle_earnings"]
            user.total_earned += result["cycle_earnings"]
            db.commit()
    
    return {
        "success": True,
        "cycle_results": result,
        "new_balance": round(current_user.balance + result["cycle_earnings"], 2),
        "message": f"💰 Earned ${result['cycle_earnings']:.2f} from coding services!"
    }


@router.get("/agents")
def get_agents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all coding agents"""
    agency = get_coding_agency()
    
    return {
        "agents": [
            {
                "id": a.agent_id,
                "name": a.name,
                "skills": a.skills,
                "hourly_rate": a.hourly_rate,
                "availability": round(a.availability, 1),
                "rating": a.rating,
                "completed_jobs": a.completed_jobs,
                "earnings": round(a.earnings_total, 2)
            }
            for a in agency.agents.values()
        ]
    }


@router.post("/a2a/broadcast-offer")
def broadcast_service_offering(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Broadcast service offering via A2A network"""
    agency = get_coding_agency()
    
    offering = agency.generate_service_offering()
    
    return {
        "success": True,
        "broadcast_sent": True,
        "offering": offering,
        "message": "📢 Service offering broadcasted to A2A network",
        "protocol": "A2A",
        "reach": "All connected agents"
    }


@router.get("/opportunities")
def get_opportunities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current coding opportunities"""
    agency = get_coding_agency()
    
    opportunities = agency.discover_opportunities()
    
    return {
        "total": len(opportunities),
        "opportunities": opportunities,
        "estimated_total_value": sum(o["budget"] for o in opportunities)
    }


@router.post("/auto-run")
def start_autonomous_coding(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Start fully autonomous coding mode"""
    agency = get_coding_agency()
    
    # Run multiple cycles
    total_earned = 0.0
    cycles_run = 0
    
    for _ in range(5):  # Run 5 cycles
        result = agency.simulate_work_cycle()
        total_earned += result["cycle_earnings"]
        cycles_run += 1
    
    # Add to user
    if total_earned > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            user.balance += total_earned
            user.total_earned += total_earned
            db.commit()
    
    return {
        "success": True,
        "mode": "AUTONOMOUS_CODING",
        "cycles_run": cycles_run,
        "total_earned": round(total_earned, 2),
        "new_balance": round(current_user.balance + total_earned, 2),
        "message": f"🤖 Autonomous coding completed! Earned ${total_earned:.2f}",
        "a2a_protocol": "active",
        "mcp_context_sharing": "enabled"
    }
