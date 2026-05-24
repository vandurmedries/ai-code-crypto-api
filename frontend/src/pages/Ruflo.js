import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Waves, Users, Bot, Send, Share2, Sparkles, Target, Network } from 'lucide-react';

const Ruflo = () => {
  const [agents, setAgents] = useState([]);
  const [swarms, setSwarms] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newAgent, setNewAgent] = useState({ name: '', type: 'earner', capabilities: '' });
  const [newSwarm, setNewSwarm] = useState({ name: '', goal: '', agentIds: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, swarmsRes, statusRes] = await Promise.all([
        axios.get('/api/ruflo/agents'),
        axios.get('/api/ruflo/swarms'),
        axios.get('/api/ruflo/status')
      ]);
      setAgents(agentsRes.data.agents || []);
      setSwarms(swarmsRes.data.swarms || []);
      setStatus(statusRes.data);
    } catch (error) {
      console.error('Ruflo fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAgent = async () => {
    try {
      await axios.post('/api/ruflo/agents/create', null, {
        params: {
          agent_type: newAgent.type,
          name: newAgent.name,
          capabilities: newAgent.capabilities,
          swarm_enabled: true
        }
      });
      setNewAgent({ name: '', type: 'earner', capabilities: '' });
      fetchData();
    } catch (error) {
      alert('Failed to create agent');
    }
  };

  const createSwarm = async () => {
    try {
      await axios.post('/api/ruflo/swarms/create', null, {
        params: {
          name: newSwarm.name,
          goal: newSwarm.goal,
          agent_ids: newSwarm.agentIds
        }
      });
      setNewSwarm({ name: '', goal: '', agentIds: '' });
      fetchData();
    } catch (error) {
      alert('Failed to create swarm');
    }
  };

  const getEarningStrategy = async () => {
    try {
      const res = await axios.get('/api/ruflo/earning-strategy');
      alert(`Strategy: ${JSON.stringify(res.data.swarm_intelligence, null, 2)}`);
    } catch (error) {
      alert('Failed to get strategy');
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
            <Waves className="w-8 h-8 text-cyan-500" />
            Ruflo
          </h1>
          <p className="text-gray-600 mt-1">Agent orchestration for Claude - Multi-agent swarms & federation</p>
        </div>
        <button 
          onClick={getEarningStrategy}
          className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-cyan-600 hover:to-blue-700"
        >
          <Sparkles className="w-5 h-5" />
          Get AI Strategy
        </button>
      </div>

      {/* Status Cards */}
      {status && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-lg shadow p-4 text-white">
            <p className="text-cyan-100 text-sm">Total Agents</p>
            <p className="text-3xl font-bold">{status.total_agents}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
            <p className="text-blue-100 text-sm">Swarms</p>
            <p className="text-3xl font-bold">{status.total_swarms}</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-4 text-white">
            <p className="text-purple-100 text-sm">Tasks</p>
            <p className="text-3xl font-bold">{status.total_tasks}</p>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
            <p className="text-green-100 text-sm">Federation</p>
            <p className="text-3xl font-bold">{status.federation_active ? 'ON' : 'OFF'}</p>
          </div>
        </div>
      )}

      {/* Create Agent */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5 text-cyan-500" />
          Create Ruflo Agent
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Agent name"
            value={newAgent.name}
            onChange={(e) => setNewAgent({...newAgent, name: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <select
            value={newAgent.type}
            onChange={(e) => setNewAgent({...newAgent, type: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="earner">Earner</option>
            <option value="trader">Trader</option>
            <option value="analyzer">Analyzer</option>
            <option value="federator">Federator</option>
            <option value="wallet_manager">Wallet Manager</option>
          </select>
          <input
            type="text"
            placeholder="Capabilities (comma-separated)"
            value={newAgent.capabilities}
            onChange={(e) => setNewAgent({...newAgent, capabilities: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button
            onClick={createAgent}
            className="bg-cyan-600 text-white px-4 py-2 rounded-lg hover:bg-cyan-700"
          >
            Create Agent
          </button>
        </div>
      </div>

      {/* Create Swarm */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Network className="w-5 h-5 text-blue-500" />
          Create Agent Swarm
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Swarm name"
            value={newSwarm.name}
            onChange={(e) => setNewSwarm({...newSwarm, name: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <input
            type="text"
            placeholder="Goal (e.g., maximize earnings)"
            value={newSwarm.goal}
            onChange={(e) => setNewSwarm({...newSwarm, goal: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <input
            type="text"
            placeholder="Agent IDs (comma-separated)"
            value={newSwarm.agentIds}
            onChange={(e) => setNewSwarm({...newSwarm, agentIds: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button
            onClick={createSwarm}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Create Swarm
          </button>
        </div>
      </div>

      {/* Agents List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5" />
          Active Agents ({agents.length})
        </h2>
        <div className="space-y-2">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-cyan-100 rounded-full">
                  <Bot className="w-5 h-5 text-cyan-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{agent.name}</p>
                  <p className="text-sm text-gray-500">{agent.type} • {agent.agent_id.slice(0,8)}</p>
                  <div className="flex gap-1 mt-1">
                    {agent.capabilities.slice(0,3).map((cap, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 bg-gray-200 rounded-full">{cap}</span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {agent.swarm_enabled && (
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">Swarm</span>
                )}
                <span className={`px-2 py-1 text-xs rounded-full ${agent.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                  {agent.status}
                </span>
              </div>
            </div>
          ))}
          {agents.length === 0 && (
            <p className="text-gray-500 text-center py-4">No agents yet. Create one above!</p>
          )}
        </div>
      </div>

      {/* Swarms List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Share2 className="w-5 h-5" />
          Active Swarms ({swarms.length})
        </h2>
        <div className="space-y-2">
          {swarms.map((swarm) => (
            <div key={swarm.swarm_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <Network className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{swarm.name}</p>
                  <p className="text-sm text-gray-500">{swarm.goal}</p>
                  <p className="text-xs text-gray-400">{swarm.agents} agents • Coord: {swarm.coordinator?.slice(0,8) || 'none'}</p>
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${swarm.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                {swarm.status}
              </span>
            </div>
          ))}
          {swarms.length === 0 && (
            <p className="text-gray-500 text-center py-4">No swarms yet. Create one above!</p>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-cyan-50 to-blue-50 border border-cyan-200 rounded-lg p-4">
          <Target className="w-8 h-8 text-cyan-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Swarm Intelligence</h3>
          <p className="text-sm text-gray-600">Multiple agents work together to optimize earnings</p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
          <Send className="w-8 h-8 text-purple-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Agent Federation</h3>
          <p className="text-sm text-gray-600">Agents communicate and share knowledge like Slack</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
          <Sparkles className="w-8 h-8 text-green-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Self-Learning</h3>
          <p className="text-sm text-gray-600">Agents improve strategies based on performance</p>
        </div>
      </div>
    </div>
  );
};

export default Ruflo;
