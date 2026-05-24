"""
A2A Protocol Router
Agent-to-Agent communication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.a2a_protocol import A2AAgent, AgentRegistry, A2AMessage
from app import models

router = APIRouter()

# Global agent registry
agent_registry = AgentRegistry()


@router.post("/agents/register")
def register_agent(
    agent_type: str,
    capabilities: List[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Register a new A2A agent"""
    agent_id = f"user_{current_user.id}_{agent_type}_{len(agent_registry.agents)}"
    
    agent = A2AAgent(
        agent_id=agent_id,
        agent_type=agent_type,
        capabilities=capabilities
    )
    
    # Register self as peer
    agent.register_peer(agent_id, f"/api/a2a/agents/{agent_id}/receive", capabilities)
    
    # Register with global registry
    agent_registry.register_agent(agent, f"/api/a2a/agents/{agent_id}/receive")
    
    return {
        "agent_id": agent_id,
        "agent_type": agent_type,
        "capabilities": capabilities,
        "status": "registered"
    }


@router.get("/agents/discover")
def discover_agents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Discover all available agents"""
    agents = []
    for agent_id, agent in agent_registry.agents.items():
        agents.append({
            "agent_id": agent_id,
            "agent_type": agent.agent_type,
            "capabilities": agent.capabilities,
            "peers": len(agent.peers)
        })
    
    return {
        "total_agents": len(agents),
        "agents": agents
    }


@router.post("/agents/{agent_id}/send")
def send_message(
    agent_id: str,
    receiver_id: str,
    message_type: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send A2A message from one agent to another"""
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify sender owns this agent
    if not agent_id.startswith(f"user_{current_user.id}_"):
        raise HTTPException(status_code=403, detail="Not authorized for this agent")
    
    success = agent.send_message(receiver_id, message_type, payload)
    
    if success:
        return {
            "status": "sent",
            "from": agent_id,
            "to": receiver_id,
            "type": message_type
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to send message")


@router.post("/agents/{agent_id}/receive")
def receive_message(
    agent_id: str,
    message: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Receive A2A message (webhook endpoint)"""
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Convert dict to A2AMessage
    a2a_msg = A2AMessage(**message)
    
    # Process message
    result = agent.receive_message(a2a_msg)
    
    return result


@router.get("/agents/{agent_id}/messages")
def get_message_history(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get message history for an agent"""
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify ownership
    if not agent_id.startswith(f"user_{current_user.id}_"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = []
    for msg in agent.message_history[-50:]:  # Last 50 messages
        messages.append({
            "message_id": msg.message_id,
            "sender": msg.sender_id,
            "receiver": msg.receiver_id,
            "type": msg.message_type,
            "timestamp": msg.timestamp
        })
    
    return {
        "agent_id": agent_id,
        "total_messages": len(agent.message_history),
        "messages": messages
    }


@router.post("/agents/{agent_id}/broadcast")
def broadcast_opportunity(
    agent_id: str,
    opportunity: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Broadcast earning opportunity to all peers"""
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if not agent_id.startswith(f"user_{current_user.id}_"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sent_count = agent.broadcast_earning_opportunity(opportunity)
    
    return {
        "broadcasted": True,
        "peers_reached": sent_count,
        "opportunity_id": opportunity.get("opportunity_id")
    }
