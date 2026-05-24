import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Radio, Send, Users, MessageSquare, Globe, Zap } from 'lucide-react';

const A2A = () => {
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newAgentType, setNewAgentType] = useState('earner');

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get('/api/a2a/agents/discover');
      setAgents(response.data.agents || []);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const registerAgent = async () => {
    try {
      const capabilities = {
        'earner': ['market_analysis', 'earning_generation'],
        'trader': ['trading', 'arbitrage'],
        'analyzer': ['data_analysis', 'prediction'],
        'wallet_manager': ['wallet_ops', 'transactions']
      };
      
      await axios.post(`/api/a2a/agents/register`, null, {
        params: {
          agent_type: newAgentType,
          capabilities: capabilities[newAgentType].join(',')
        }
      });
      fetchAgents();
    } catch (error) {
      alert('Failed to register agent');
    }
  };

  const broadcastOpportunity = async () => {
    if (agents.length === 0) {
      alert('No agents registered');
      return;
    }
    
    try {
      const agentId = agents[0].agent_id;
      await axios.post(`/api/a2a/agents/${agentId}/broadcast`, {
        opportunity_id: `opp_${Date.now()}`,
        potential_earning: 15.50,
        type: 'crypto_arbitrage',
        confidence: 0.85
      });
      alert('Earning opportunity broadcasted to all agents!');
    } catch (error) {
      alert('Broadcast failed');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Radio className="w-8 h-8 text-purple-500" />
            A2A Protocol
          </h1>
          <p className="text-gray-600 mt-1">Agent-to-Agent communication network</p>
        </div>
        <button 
          onClick={broadcastOpportunity}
          className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
        >
          <Send className="w-5 h-5" />
          Broadcast Opportunity
        </button>
      </div>

      {/* Register New Agent */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Register New Agent</h2>
        <div className="flex gap-4">
          <select 
            value={newAgentType} 
            onChange={(e) => setNewAgentType(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="earner">Earner (Market Analysis + Earning)</option>
            <option value="trader">Trader (Trading + Arbitrage)</option>
            <option value="analyzer">Analyzer (Data + Prediction)</option>
            <option value="wallet_manager">Wallet Manager (Wallet Ops)</option>
          </select>
          <button 
            onClick={registerAgent}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            <Users className="w-5 h-5" />
            Register Agent
          </button>
        </div>
      </div>

      {/* Active Agents */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Active Agents ({agents.length})
        </h2>
        
        <div className="space-y-3">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-100 rounded-full">
                  <Zap className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{agent.agent_id}</p>
                  <p className="text-sm text-gray-500">Type: {agent.agent_type}</p>
                  <div className="flex gap-2 mt-1">
                    {agent.capabilities.map((cap, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Peers</p>
                <p className="font-semibold text-gray-900">{agent.peers}</p>
              </div>
            </div>
          ))}
          
          {agents.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Radio className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p>No agents registered yet</p>
              <p className="text-sm mt-1">Create your first agent above</p>
            </div>
          )}
        </div>
      </div>

      {/* Message Types */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <MessageSquare className="w-8 h-8 text-green-600 mb-2" />
          <h3 className="font-semibold text-gray-900">earning_opportunity</h3>
          <p className="text-sm text-gray-600">Share earning opportunities with other agents</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <MessageSquare className="w-8 h-8 text-blue-600 mb-2" />
          <h3 className="font-semibold text-gray-900">market_data</h3>
          <p className="text-sm text-gray-600">Broadcast market trends and analysis</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <MessageSquare className="w-8 h-8 text-orange-600 mb-2" />
          <h3 className="font-semibold text-gray-900">trade_signal</h3>
          <p className="text-sm text-gray-600">Send trading signals and alerts</p>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-gray-900 text-white rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">How A2A Protocol Works</h2>
        <ol className="space-y-2 text-gray-300">
          <li>1. <strong>Register Agents:</strong> Create specialized AI agents with specific capabilities</li>
          <li>2. <strong>Discover Peers:</strong> Agents automatically discover each other in the network</li>
          <li>3. <strong>Send Messages:</strong> Agents communicate via standardized message types</li>
          <li>4. <strong>Broadcast:</strong> Share earning opportunities across the entire network</li>
          <li>5. <strong>Verify:</strong> All messages are cryptographically signed for security</li>
        </ol>
      </div>
    </div>
  );
};

export default A2A;
