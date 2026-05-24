"""
Ruflo Integration Service
Connects AI Earning Platform with Ruflo agent orchestration
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum


class RufloAgentType(str, Enum):
    """Ruflo agent types for earning platform"""
    EARNER = "earner"
    TRADER = "trader"
    ANALYZER = "analyzer"
    FEDERATOR = "federator"
    WALLET_MANAGER = "wallet_manager"


class RufloAgent(BaseModel):
    """Ruflo agent definition"""
    agent_id: str
    agent_type: RufloAgentType
    name: str
    capabilities: List[str]
    memory_enabled: bool = True
    swarm_enabled: bool = False
    federation_id: Optional[str] = None
    created_at: str
    status: str = "active"
    config: Dict[str, Any] = {}


class RufloSwarm(BaseModel):
    """Ruflo swarm of agents"""
    swarm_id: str
    name: str
    agents: List[str]  # agent_ids
    coordinator_id: Optional[str]
    goal: str
    status: str = "active"
    created_at: str


class RufloTask(BaseModel):
    """Task for Ruflo agents"""
    task_id: str
    agent_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 5
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: str
    completed_at: Optional[str] = None


class RufloIntegration:
    """Main Ruflo integration class"""
    
    def __init__(self, platform_id: str = "ai_earning_platform"):
        self.platform_id = platform_id
        self.agents: Dict[str, RufloAgent] = {}
        self.swarms: Dict[str, RufloSwarm] = {}
        self.tasks: Dict[str, RufloTask] = {}
        self.mcp_server_url: Optional[str] = None
        
    def create_agent(
        self,
        agent_type: RufloAgentType,
        name: str,
        capabilities: List[str],
        swarm_enabled: bool = False,
        config: Dict[str, Any] = None
    ) -> RufloAgent:
        """Create a new Ruflo agent"""
        agent_id = hashlib.sha256(
            f"{self.platform_id}_{name}_{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:16]
        
        agent = RufloAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name,
            capabilities=capabilities,
            swarm_enabled=swarm_enabled,
            created_at=datetime.utcnow().isoformat(),
            config=config or {}
        )
        
        self.agents[agent_id] = agent
        return agent
    
    def create_swarm(
        self,
        name: str,
        agent_ids: List[str],
        goal: str
    ) -> RufloSwarm:
        """Create a swarm of agents"""
        swarm_id = hashlib.sha256(
            f"swarm_{name}_{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:12]
        
        # Validate agents exist
        valid_agents = [aid for aid in agent_ids if aid in self.agents]
        
        # Set first agent as coordinator
        coordinator = valid_agents[0] if valid_agents else None
        
        swarm = RufloSwarm(
            swarm_id=swarm_id,
            name=name,
            agents=valid_agents,
            coordinator_id=coordinator,
            goal=goal,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.swarms[swarm_id] = swarm
        
        # Enable swarm on agents
        for agent_id in valid_agents:
            if agent_id in self.agents:
                self.agents[agent_id].swarm_enabled = True
                self.agents[agent_id].federation_id = swarm_id
        
        return swarm
    
    def submit_task(
        self,
        agent_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 5
    ) -> RufloTask:
        """Submit a task to an agent"""
        task_id = hashlib.sha256(
            f"task_{agent_id}_{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:12]
        
        task = RufloTask(
            task_id=task_id,
            agent_id=agent_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.tasks[task_id] = task
        return task
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark a task as completed with result"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = "completed"
        task.result = result
        task.completed_at = datetime.utcnow().isoformat()
        
        return True
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status and info"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        tasks = [t for t in self.tasks.values() if t.agent_id == agent_id]
        
        return {
            "agent": agent.dict(),
            "total_tasks": len(tasks),
            "pending_tasks": len([t for t in tasks if t.status == "pending"]),
            "completed_tasks": len([t for t in tasks if t.status == "completed"])
        }
    
    def get_swarm_status(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get swarm status"""
        if swarm_id not in self.swarms:
            return None
        
        swarm = self.swarms[swarm_id]
        agent_statuses = []
        
        for agent_id in swarm.agents:
            status = self.get_agent_status(agent_id)
            if status:
                agent_statuses.append(status)
        
        return {
            "swarm": swarm.dict(),
            "agents": agent_statuses,
            "total_agents": len(swarm.agents),
            "active_agents": len([a for a in agent_statuses 
                                 if a["agent"]["status"] == "active"])
        }
    
    def federate_message(
        self,
        sender_id: str,
        receiver_ids: List[str],
        message_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send federation message between agents (Ruflo style)"""
        if sender_id not in self.agents:
            return False
        
        message = {
            "id": hashlib.sha256(f"{sender_id}_{datetime.utcnow().timestamp()}".encode()).hexdigest()[:16],
            "sender": sender_id,
            "receivers": receiver_ids,
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "protocol": "ruflo_federation"
        }
        
        # In real implementation, this would send to Ruflo MCP server
        # For now, we store it as a task for each receiver
        for receiver_id in receiver_ids:
            if receiver_id in self.agents:
                self.submit_task(
                    agent_id=receiver_id,
                    task_type=f"federation_{message_type}",
                    payload=message,
                    priority=7
                )
        
        return True
    
    def get_earning_swarm_recommendation(self, user_balance: float) -> Dict[str, Any]:
        """Get earning strategy from Ruflo swarm"""
        # Simulate swarm intelligence for earning
        strategies = []
        
        for swarm_id, swarm in self.swarms.items():
            if "earn" in swarm.goal.lower() or "profit" in swarm.goal.lower():
                strategies.append({
                    "swarm_id": swarm_id,
                    "name": swarm.name,
                    "agents": len(swarm.agents),
                    "recommendation": f"Swarm '{swarm.name}' suggests diversified earning based on ${user_balance} balance",
                    "confidence": 0.75 + (len(swarm.agents) * 0.05)
                })
        
        if not strategies:
            return {
                "message": "No earning swarms active",
                "recommendation": "Create an earning swarm first",
                "action": "create_swarm"
            }
        
        # Return best strategy
        best = max(strategies, key=lambda x: x["confidence"])
        return {
            "best_strategy": best,
            "all_strategies": strategies,
            "swarm_intelligence_active": True
        }


# Singleton instance
_ruflo_instance: Optional[RufloIntegration] = None

def get_ruflo_integration() -> RufloIntegration:
    """Get or create Ruflo integration instance"""
    global _ruflo_instance
    if _ruflo_instance is None:
        _ruflo_instance = RufloIntegration()
    return _ruflo_instance
