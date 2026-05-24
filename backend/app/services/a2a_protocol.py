"""
A2A (Agent-to-Agent) Protocol Implementation
Enables communication between AI agents in the earning platform
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class A2AMessage(BaseModel):
    """A2A Message format for agent communication"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str  # 'earning_opportunity', 'market_data', 'trade_signal', 'wallet_update'
    payload: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None


class A2AAgent:
    """Agent that can communicate with other agents via A2A protocol"""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type  # 'earner', 'trader', 'analyzer', 'wallet_manager'
        self.capabilities = capabilities
        self.peers: Dict[str, Dict] = {}  # Known peer agents
        self.message_history: List[A2AMessage] = []
        
    def register_peer(self, peer_id: str, peer_endpoint: str, peer_capabilities: List[str]):
        """Register another agent as a peer"""
        self.peers[peer_id] = {
            'endpoint': peer_endpoint,
            'capabilities': peer_capabilities,
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
    def create_message(self, receiver_id: str, message_type: str, payload: Dict) -> A2AMessage:
        """Create a new A2A message"""
        message_id = hashlib.sha256(
            f"{self.agent_id}_{receiver_id}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        message = A2AMessage(
            message_id=message_id,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Sign the message (simplified - in production use proper crypto)
        message.signature = hashlib.sha256(
            f"{message_id}{self.agent_id}{receiver_id}{json.dumps(payload)}".encode()
        ).hexdigest()[:32]
        
        return message
    
    def send_message(self, receiver_id: str, message_type: str, payload: Dict) -> bool:
        """Send message to a peer agent"""
        if receiver_id not in self.peers:
            return False
            
        message = self.create_message(receiver_id, message_type, payload)
        self.message_history.append(message)
        
        # In production: HTTP POST to peer endpoint
        # For now: simulate successful delivery
        return True
    
    def receive_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Process incoming A2A message"""
        self.message_history.append(message)
        
        # Verify signature
        expected_sig = hashlib.sha256(
            f"{message.message_id}{message.sender_id}{message.receiver_id}{json.dumps(message.payload)}".encode()
        ).hexdigest()[:32]
        
        if message.signature != expected_sig:
            return {'status': 'error', 'message': 'Invalid signature'}
        
        # Process based on message type
        handlers = {
            'earning_opportunity': self._handle_earning_opportunity,
            'market_data': self._handle_market_data,
            'trade_signal': self._handle_trade_signal,
            'wallet_update': self._handle_wallet_update,
            'price_alert': self._handle_price_alert
        }
        
        handler = handlers.get(message.message_type, self._handle_unknown)
        return handler(message.payload)
    
    def _handle_earning_opportunity(self, payload: Dict) -> Dict:
        """Handle earning opportunity message"""
        return {
            'status': 'processed',
            'action': 'opportunity_recorded',
            'opportunity_id': payload.get('opportunity_id'),
            'potential_earning': payload.get('potential_earning')
        }
    
    def _handle_market_data(self, payload: Dict) -> Dict:
        """Handle market data broadcast"""
        return {
            'status': 'processed',
            'action': 'market_data_stored',
            'source': payload.get('source'),
            'trend_count': len(payload.get('trends', []))
        }
    
    def _handle_trade_signal(self, payload: Dict) -> Dict:
        """Handle trade signal from another agent"""
        return {
            'status': 'processed',
            'action': 'signal_evaluated',
            'signal': payload.get('signal'),
            'confidence': payload.get('confidence')
        }
    
    def _handle_wallet_update(self, payload: Dict) -> Dict:
        """Handle wallet balance update"""
        return {
            'status': 'processed',
            'action': 'balance_updated',
            'wallet_id': payload.get('wallet_id'),
            'new_balance': payload.get('new_balance')
        }
    
    def _handle_price_alert(self, payload: Dict) -> Dict:
        """Handle cryptocurrency price alert"""
        return {
            'status': 'processed',
            'action': 'alert_triggered',
            'currency': payload.get('currency'),
            'price': payload.get('price'),
            'threshold': payload.get('threshold')
        }
    
    def _handle_unknown(self, payload: Dict) -> Dict:
        """Handle unknown message type"""
        return {
            'status': 'error',
            'message': 'Unknown message type'
        }
    
    def discover_agents(self) -> List[Dict]:
        """Discover available agents in the network"""
        # In production: query agent registry/directory
        # For now: return known peers
        return [
            {
                'agent_id': peer_id,
                'capabilities': info['capabilities'],
                'status': info['status']
            }
            for peer_id, info in self.peers.items()
        ]
    
    def broadcast_earning_opportunity(self, opportunity: Dict) -> int:
        """Broadcast earning opportunity to all peer agents"""
        sent_count = 0
        for peer_id in self.peers:
            if self.send_message(peer_id, 'earning_opportunity', opportunity):
                sent_count += 1
        return sent_count


class AgentRegistry:
    """Registry for managing agent discovery and registration"""
    
    def __init__(self):
        self.agents: Dict[str, A2AAgent] = {}
        self.agent_endpoints: Dict[str, str] = {}
        
    def register_agent(self, agent: A2AAgent, endpoint: str):
        """Register an agent with the registry"""
        self.agents[agent.agent_id] = agent
        self.agent_endpoints[agent.agent_id] = endpoint
        
    def get_agent(self, agent_id: str) -> Optional[A2AAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents_by_capability(self, capability: str) -> List[A2AAgent]:
        """Find agents with specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]
    
    def route_message(self, message: A2AMessage) -> bool:
        """Route message to target agent"""
        target_agent = self.agents.get(message.receiver_id)
        if target_agent:
            target_agent.receive_message(message)
            return True
        return False
