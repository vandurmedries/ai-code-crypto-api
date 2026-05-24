"""
MCP (Model Context Protocol) Router
Context sharing endpoints for AI models
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.mcp_protocol import (
    MCPClient, MCPServer, MCPContext, ContextType,
    create_market_context, create_earning_context, create_wallet_context
)
from app import models

router = APIRouter()

# Global MCP server
mcp_server = MCPServer()

# Store clients by user
user_clients: Dict[int, MCPClient] = {}


def get_or_create_client(user_id: int, user_email: str) -> MCPClient:
    """Get or create MCP client for user"""
    if user_id not in user_clients:
        client = MCPClient(
            model_id=f"user_{user_id}",
            model_name=f"user_{user_email}"
        )
        user_clients[user_id] = client
        mcp_server.register_client(client)
    return user_clients[user_id]


@router.post("/context/create")
def create_context(
    context_type: str,
    payload: Dict[str, Any],
    target_models: Optional[List[str]] = None,
    priority: int = 5,
    ttl: int = 3600,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new MCP context"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    try:
        ctx_type = ContextType(context_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid context type: {context_type}")
    
    context = client.create_context(
        context_type=ctx_type,
        payload=payload,
        target_models=target_models,
        priority=priority,
        ttl=ttl
    )
    
    # Share with server
    mcp_server.broadcast_context(context)
    
    return {
        "context_id": context.context_id,
        "context_type": context_type,
        "source": client.model_id,
        "timestamp": context.timestamp,
        "priority": priority
    }


@router.get("/contexts")
def get_contexts(
    context_type: Optional[str] = None,
    min_priority: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all contexts for current user"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    # Convert string to enum if provided
    ctx_type = None
    if context_type:
        try:
            ctx_type = ContextType(context_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid context type: {context_type}")
    
    contexts = client.query_contexts(
        context_type=ctx_type,
        min_priority=min_priority
    )
    
    # Also get from server
    server_contexts = mcp_server.get_shared_contexts(
        model_id=client.model_id,
        context_type=ctx_type
    )
    
    # Merge and deduplicate
    all_contexts = {ctx.context_id: ctx for ctx in contexts}
    for ctx in server_contexts:
        if ctx.context_id not in all_contexts:
            all_contexts[ctx.context_id] = ctx
    
    result = []
    for ctx in all_contexts.values():
        result.append({
            "context_id": ctx.context_id,
            "context_type": ctx.context_type.value,
            "source_model": ctx.source_model,
            "priority": ctx.priority,
            "timestamp": ctx.timestamp,
            "payload_preview": str(ctx.payload)[:100] + "..." if len(str(ctx.payload)) > 100 else str(ctx.payload)
        })
    
    # Sort by priority desc
    result.sort(key=lambda x: x["priority"], reverse=True)
    
    return {
        "total": len(result),
        "contexts": result
    }


@router.get("/context/{context_id}")
def get_context(
    context_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get specific context by ID"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    context = client.get_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found or expired")
    
    return {
        "context_id": context.context_id,
        "context_type": context.context_type.value,
        "source_model": context.source_model,
        "target_models": context.target_models,
        "payload": context.payload,
        "timestamp": context.timestamp,
        "priority": context.priority,
        "ttl": context.ttl
    }


@router.post("/context/market-data")
def share_market_data(
    trends: List[Dict[str, Any]],
    source: str = "market_analyzer",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Share market data via MCP"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    context = create_market_context(client, trends, source)
    mcp_server.broadcast_context(context)
    
    return {
        "shared": True,
        "context_id": context.context_id,
        "trend_count": len(trends),
        "target_models": context.target_models
    }


@router.post("/context/earning")
def share_earning_opportunity(
    opportunity: Dict[str, Any],
    confidence: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Share earning opportunity via MCP"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    context = create_earning_context(client, opportunity, confidence)
    mcp_server.broadcast_context(context)
    
    return {
        "shared": True,
        "context_id": context.context_id,
        "confidence": confidence,
        "auto_execute": confidence > 0.7,
        "priority": context.priority
    }


@router.post("/context/wallet")
def share_wallet_update(
    wallet_id: str,
    balance: float,
    currency: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Share wallet balance update via MCP"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    context = create_wallet_context(client, wallet_id, balance, currency)
    mcp_server.broadcast_context(context)
    
    return {
        "shared": True,
        "context_id": context.context_id,
        "wallet_id": wallet_id,
        "balance": balance,
        "currency": currency
    }


@router.get("/server/stats")
def get_server_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get MCP server statistics"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    # Clean expired contexts
    expired_count = client.clear_expired()
    
    return {
        "registered_clients": len(mcp_server.clients),
        "global_contexts": len(mcp_server.global_contexts),
        "user_contexts": len(client.context_store),
        "expired_cleared": expired_count,
        "context_types": [ct.value for ct in ContextType]
    }


@router.post("/sync")
def sync_contexts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Sync all relevant contexts from server to client"""
    client = get_or_create_client(current_user.id, current_user.email)
    
    success = mcp_server.sync_client_contexts(client.model_id)
    
    return {
        "synced": success,
        "client_id": client.model_id,
        "local_contexts": len(client.context_store)
    }
