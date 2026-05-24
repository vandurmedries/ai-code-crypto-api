"""
Ruflo Router
Agent orchestration endpoints via Ruflo integration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.ruflo_integration import (
    get_ruflo_integration, RufloAgentType, RufloAgent, RufloSwarm
)
from app import models

router = APIRouter()


@router.get("/agents")
def list_agents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all Ruflo agents"""
    ruflo = get_ruflo_integration()
    
    agents = []
    for agent_id, agent in ruflo.agents.items():
        agents.append({
            "agent_id": agent_id,
            "name": agent.name,
            "type": agent.agent_type.value,
            "capabilities": agent.capabilities,
            "swarm_enabled": agent.swarm_enabled,
            "status": agent.status,
            "created_at": agent.created_at
        })
    
    return {
        "total_agents": len(agents),
        "agents": agents
    }


@router.post("/agents/create")
def create_agent(
    agent_type: str,
    name: str,
    capabilities: str,  # comma-separated
    swarm_enabled: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new Ruflo agent"""
    ruflo = get_ruflo_integration()
    
    try:
        agent_type_enum = RufloAgentType(agent_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    
    caps = [c.strip() for c in capabilities.split(",")]
    
    agent = ruflo.create_agent(
        agent_type=agent_type_enum,
        name=name,
        capabilities=caps,
        swarm_enabled=swarm_enabled,
        config={"owner_id": current_user.id}
    )
    
    return {
        "success": True,
        "agent": {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "type": agent.agent_type.value,
            "capabilities": agent.capabilities,
            "swarm_enabled": agent.swarm_enabled
        }
    }


@router.get("/agents/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get agent details and status"""
    ruflo = get_ruflo_integration()
    
    status = ruflo.get_agent_status(agent_id)
    if not status:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return status


@router.post("/agents/{agent_id}/task")
def submit_task(
    agent_id: str,
    task_type: str,
    payload: Dict[str, Any],
    priority: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Submit a task to an agent"""
    ruflo = get_ruflo_integration()
    
    if agent_id not in ruflo.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    task = ruflo.submit_task(
        agent_id=agent_id,
        task_type=task_type,
        payload=payload,
        priority=priority
    )
    
    return {
        "success": True,
        "task_id": task.task_id,
        "status": task.status,
        "agent_id": agent_id
    }


@router.get("/swarms")
def list_swarms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all agent swarms"""
    ruflo = get_ruflo_integration()
    
    swarms = []
    for swarm_id, swarm in ruflo.swarms.items():
        swarms.append({
            "swarm_id": swarm_id,
            "name": swarm.name,
            "goal": swarm.goal,
            "agents": len(swarm.agents),
            "coordinator": swarm.coordinator_id,
            "status": swarm.status,
            "created_at": swarm.created_at
        })
    
    return {
        "total_swarms": len(swarms),
        "swarms": swarms
    }


@router.post("/swarms/create")
def create_swarm(
    name: str,
    agent_ids: str,  # comma-separated
    goal: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new agent swarm"""
    ruflo = get_ruflo_integration()
    
    agent_list = [a.strip() for a in agent_ids.split(",")]
    
    swarm = ruflo.create_swarm(
        name=name,
        agent_ids=agent_list,
        goal=goal
    )
    
    return {
        "success": True,
        "swarm": {
            "swarm_id": swarm.swarm_id,
            "name": swarm.name,
            "goal": swarm.goal,
            "agents": swarm.agents,
            "coordinator": swarm.coordinator_id
        }
    }


@router.get("/swarms/{swarm_id}")
def get_swarm(
    swarm_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get swarm details and status"""
    ruflo = get_ruflo_integration()
    
    status = ruflo.get_swarm_status(swarm_id)
    if not status:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    return status


@router.post("/federate")
def federate_message(
    sender_id: str,
    receiver_ids: str,  # comma-separated
    message_type: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send federation message between agents"""
    ruflo = get_ruflo_integration()
    
    receivers = [r.strip() for r in receiver_ids.split(",")]
    
    success = ruflo.federate_message(
        sender_id=sender_id,
        receiver_ids=receivers,
        message_type=message_type,
        payload=payload
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Federation failed")
    
    return {
        "success": True,
        "sender": sender_id,
        "receivers": receivers,
        "message_type": message_type,
        "protocol": "ruflo_federation"
    }


@router.get("/earning-strategy")
def get_earning_strategy(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get earning strategy from Ruflo swarm intelligence"""
    ruflo = get_ruflo_integration()
    
    strategy = ruflo.get_earning_swarm_recommendation(
        user_balance=current_user.balance
    )
    
    return {
        "user_id": current_user.id,
        "balance": current_user.balance,
        "swarm_intelligence": strategy
    }


@router.get("/status")
def get_ruflo_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get overall Ruflo integration status"""
    ruflo = get_ruflo_integration()
    
    return {
        "platform_id": ruflo.platform_id,
        "total_agents": len(ruflo.agents),
        "total_swarms": len(ruflo.swarms),
        "total_tasks": len(ruflo.tasks),
        "mcp_server_connected": ruflo.mcp_server_url is not None,
        "federation_active": len(ruflo.swarms) > 0,
        "agent_types": [t.value for t in RufloAgentType]
    }
