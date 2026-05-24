"""
MCP (Model Context Protocol) Implementation
Standardized context sharing between AI models in the earning platform
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel
from enum import Enum


class ContextType(str, Enum):
    """Types of context that can be shared via MCP"""
    MARKET_DATA = "market_data"
    USER_PREFERENCES = "user_preferences"
    EARNING_HISTORY = "earning_history"
    WALLET_BALANCE = "wallet_balance"
    TRADE_SIGNAL = "trade_signal"
    RISK_PROFILE = "risk_profile"
    ML_PREDICTION = "ml_prediction"


class MCPContext(BaseModel):
    """MCP Context container for standardized data sharing"""
    context_id: str
    context_type: ContextType
    source_model: str  # Which model/AI created this context
    target_models: List[str]  # Which models should receive this
    payload: Dict[str, Any]
    timestamp: str
    ttl: int = 3600  # Time to live in seconds
    priority: int = 5  # 1-10, higher = more important


class MCPClient:
    """Client for interacting with MCP protocol"""
    
    def __init__(self, model_id: str, model_name: str):
        self.model_id = model_id
        self.model_name = model_name
        self.context_store: Dict[str, MCPContext] = {}
        self.subscribers: Dict[ContextType, List[Callable]] = {}
        
    def create_context(
        self, 
        context_type: ContextType, 
        payload: Dict[str, Any],
        target_models: List[str] = None,
        priority: int = 5,
        ttl: int = 3600
    ) -> MCPContext:
        """Create a new MCP context"""
        context_id = f"{self.model_id}_{context_type.value}_{datetime.utcnow().timestamp()}"
        
        context = MCPContext(
            context_id=context_id,
            context_type=context_type,
            source_model=self.model_id,
            target_models=target_models or ["all"],
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
            ttl=ttl,
            priority=priority
        )
        
        self.context_store[context_id] = context
        return context
    
    def share_context(self, context: MCPContext) -> bool:
        """Share context with other models"""
        # Store in local registry
        self.context_store[context.context_id] = context
        
        # Notify subscribers
        if context.context_type in self.subscribers:
            for callback in self.subscribers[context.context_type]:
                try:
                    callback(context)
                except Exception as e:
                    print(f"MCP subscriber error: {e}")
        
        return True
    
    def subscribe(self, context_type: ContextType, callback: Callable):
        """Subscribe to specific context type updates"""
        if context_type not in self.subscribers:
            self.subscribers[context_type] = []
        self.subscribers[context_type].append(callback)
    
    def get_context(self, context_id: str) -> Optional[MCPContext]:
        """Retrieve context by ID"""
        context = self.context_store.get(context_id)
        if context:
            # Check if expired
            age = (datetime.utcnow() - datetime.fromisoformat(context.timestamp)).total_seconds()
            if age > context.ttl:
                del self.context_store[context_id]
                return None
        return context
    
    def query_contexts(
        self, 
        context_type: Optional[ContextType] = None,
        min_priority: int = 0,
        source_model: Optional[str] = None
    ) -> List[MCPContext]:
        """Query contexts with filters"""
        results = []
        
        for context in self.context_store.values():
            # Check expired
            age = (datetime.utcnow() - datetime.fromisoformat(context.timestamp)).total_seconds()
            if age > context.ttl:
                continue
                
            # Apply filters
            if context_type and context.context_type != context_type:
                continue
            if context.priority < min_priority:
                continue
            if source_model and context.source_model != source_model:
                continue
                
            results.append(context)
        
        # Sort by priority (desc) then timestamp (desc)
        results.sort(key=lambda x: (-x.priority, x.timestamp), reverse=True)
        return results
    
    def delete_context(self, context_id: str) -> bool:
        """Delete a context"""
        if context_id in self.context_store:
            del self.context_store[context_id]
            return True
        return False
    
    def clear_expired(self) -> int:
        """Clear expired contexts, returns count deleted"""
        expired = []
        for context_id, context in self.context_store.items():
            age = (datetime.utcnow() - datetime.fromisoformat(context.timestamp)).total_seconds()
            if age > context.ttl:
                expired.append(context_id)
        
        for context_id in expired:
            del self.context_store[context_id]
        
        return len(expired)


class MCPServer:
    """MCP Server for centralized context management"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.global_contexts: Dict[str, MCPContext] = {}
        
    def register_client(self, client: MCPClient):
        """Register an MCP client"""
        self.clients[client.model_id] = client
        
    def broadcast_context(self, context: MCPContext) -> int:
        """Broadcast context to all relevant clients"""
        delivered = 0
        
        for client in self.clients.values():
            # Check if this client should receive
            if "all" in context.target_models or client.model_id in context.target_models:
                client.share_context(context)
                delivered += 1
        
        # Also store globally
        self.global_contexts[context.context_id] = context
        
        return delivered
    
    def get_shared_contexts(
        self, 
        model_id: str,
        context_type: Optional[ContextType] = None
    ) -> List[MCPContext]:
        """Get all contexts relevant to a specific model"""
        results = []
        
        for context in self.global_contexts.values():
            # Check expired
            age = (datetime.utcnow() - datetime.fromisoformat(context.timestamp)).total_seconds()
            if age > context.ttl:
                continue
            
            # Check if relevant to this model
            if "all" not in context.target_models and model_id not in context.target_models:
                continue
            
            if context_type and context.context_type != context_type:
                continue
            
            results.append(context)
        
        return sorted(results, key=lambda x: (-x.priority, x.timestamp))
    
    def sync_client_contexts(self, model_id: str) -> bool:
        """Sync server contexts to a specific client"""
        client = self.clients.get(model_id)
        if not client:
            return False
        
        contexts = self.get_shared_contexts(model_id)
        for context in contexts:
            client.share_context(context)
        
        return True


# Convenience functions for earning platform

def create_market_context(
    mcp_client: MCPClient,
    trends: List[Dict],
    source: str = "market_analyzer"
) -> MCPContext:
    """Create standardized market data context"""
    return mcp_client.create_context(
        context_type=ContextType.MARKET_DATA,
        payload={
            "trends": trends,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        },
        target_models=["earner", "trader", "risk_manager"],
        priority=8
    )

def create_earning_context(
    mcp_client: MCPClient,
    opportunity: Dict,
    confidence: float
) -> MCPContext:
    """Create earning opportunity context"""
    return mcp_client.create_context(
        context_type=ContextType.EARNING_HISTORY,
        payload={
            "opportunity": opportunity,
            "confidence": confidence,
            "auto_execute": confidence > 0.7
        },
        target_models=["executor", "risk_manager"],
        priority=9 if confidence > 0.8 else 6
    )

def create_wallet_context(
    mcp_client: MCPClient,
    wallet_id: str,
    balance: float,
    currency: str
) -> MCPContext:
    """Create wallet balance context"""
    return mcp_client.create_context(
        context_type=ContextType.WALLET_BALANCE,
        payload={
            "wallet_id": wallet_id,
            "balance": balance,
            "currency": currency,
            "updated_at": datetime.utcnow().isoformat()
        },
        target_models=["all"],
        priority=7
    )
