import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Share2, Database, Layers, ArrowRight, RefreshCw, Activity } from 'lucide-react';

const MCP = () => {
  const [contexts, setContexts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [contextType, setContextType] = useState('market_data');
  const [priority, setPriority] = useState(5);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [contextsRes, statsRes] = await Promise.all([
        axios.get('/api/mcp/contexts'),
        axios.get('/api/mcp/server/stats')
      ]);
      setContexts(contextsRes.data.contexts || []);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch MCP data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createContext = async () => {
    try {
      const payloads = {
        'market_data': { trends: [{ type: 'crypto', strength: 0.8, direction: 'up' }], source: 'user' },
        'earning_history': { opportunity: { type: 'arbitrage', potential: 25.5 }, confidence: 0.75 },
        'wallet_balance': { wallet_id: 'wallet_1', balance: 1.5, currency: 'BTC' },
        'trade_signal': { signal: 'buy', confidence: 0.85, asset: 'BTC/USDT' },
        'risk_profile': { risk_level: 'moderate', max_exposure: 1000 },
        'ml_prediction': { prediction: 'bullish', confidence: 0.82 }
      };

      await axios.post(`/api/mcp/context/create`, null, {
        params: {
          context_type: contextType,
          priority: priority,
          target_models: 'all'
        },
        data: payloads[contextType]
      });
      fetchData();
    } catch (error) {
      alert('Failed to create context');
    }
  };

  const shareMarketData = async () => {
    try {
      await axios.post('/api/mcp/context/market-data', {
        trends: [
          { type: 'crypto', strength: 0.85, change: '+5.2%' },
          { type: 'defi', strength: 0.72, change: '+3.1%' }
        ],
        source: 'manual_share'
      });
      fetchData();
    } catch (error) {
      alert('Failed to share market data');
    }
  };

  const syncContexts = async () => {
    try {
      await axios.post('/api/mcp/sync');
      fetchData();
    } catch (error) {
      alert('Sync failed');
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
            <Share2 className="w-8 h-8 text-blue-500" />
            MCP Protocol
          </h1>
          <p className="text-gray-600 mt-1">Model Context Protocol - Standardized context sharing between AI models</p>
        </div>
        <button 
          onClick={syncContexts}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <RefreshCw className="w-5 h-5" />
          Sync Contexts
        </button>
      </div>

      {/* Server Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg shadow p-4 text-white">
            <p className="text-blue-200 text-sm">Registered Clients</p>
            <p className="text-3xl font-bold">{stats.registered_clients}</p>
          </div>
          <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg shadow p-4 text-white">
            <p className="text-green-200 text-sm">Global Contexts</p>
            <p className="text-3xl font-bold">{stats.global_contexts}</p>
          </div>
          <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg shadow p-4 text-white">
            <p className="text-purple-200 text-sm">Your Contexts</p>
            <p className="text-3xl font-bold">{stats.user_contexts}</p>
          </div>
          <div className="bg-gradient-to-br from-orange-600 to-orange-700 rounded-lg shadow p-4 text-white">
            <p className="text-orange-200 text-sm">Context Types</p>
            <p className="text-3xl font-bold">{stats.context_types?.length || 0}</p>
          </div>
        </div>
      )}

      {/* Create Context */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Create MCP Context</h2>
        <div className="flex gap-4 mb-4">
          <select 
            value={contextType} 
            onChange={(e) => setContextType(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="market_data">Market Data</option>
            <option value="earning_history">Earning History</option>
            <option value="wallet_balance">Wallet Balance</option>
            <option value="trade_signal">Trade Signal</option>
            <option value="risk_profile">Risk Profile</option>
            <option value="ml_prediction">ML Prediction</option>
          </select>
          <select 
            value={priority} 
            onChange={(e) => setPriority(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value={1}>Priority 1 (Low)</option>
            <option value={5}>Priority 5 (Normal)</option>
            <option value={8}>Priority 8 (High)</option>
            <option value={10}>Priority 10 (Critical)</option>
          </select>
          <button 
            onClick={createContext}
            className="flex items-center gap-2 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
          >
            <Layers className="w-5 h-5" />
            Create Context
          </button>
        </div>
        <button 
          onClick={shareMarketData}
          className="w-full flex items-center justify-center gap-2 bg-blue-100 text-blue-700 py-2 rounded-lg hover:bg-blue-200"
        >
          <Activity className="w-5 h-5" />
          Quick Share: Market Data
        </button>
      </div>

      {/* Active Contexts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Contexts ({contexts.length})</h2>
        
        <div className="space-y-3">
          {contexts.map((ctx) => (
            <div key={ctx.context_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${
                  ctx.context_type === 'market_data' ? 'bg-blue-100' :
                  ctx.context_type === 'earning_history' ? 'bg-green-100' :
                  ctx.context_type === 'wallet_balance' ? 'bg-orange-100' :
                  'bg-purple-100'
                }`}>
                  <Database className={`w-6 h-6 ${
                    ctx.context_type === 'market_data' ? 'text-blue-600' :
                    ctx.context_type === 'earning_history' ? 'text-green-600' :
                    ctx.context_type === 'wallet_balance' ? 'text-orange-600' :
                    'text-purple-600'
                  }`} />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{ctx.context_type}</p>
                  <p className="text-sm text-gray-500">From: {ctx.source_model}</p>
                  <p className="text-xs text-gray-400 mt-1">{ctx.payload_preview}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`px-3 py-1 rounded-full text-sm ${
                  ctx.priority >= 8 ? 'bg-red-100 text-red-800' :
                  ctx.priority >= 5 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  Priority {ctx.priority}
                </div>
                <p className="text-xs text-gray-400 mt-1">{new Date(ctx.timestamp).toLocaleString()}</p>
              </div>
            </div>
          ))}
          
          {contexts.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p>No contexts yet</p>
              <p className="text-sm mt-1">Create your first context above</p>
            </div>
          )}
        </div>
      </div>

      {/* How it works */}
      <div className="bg-gray-900 text-white rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">How MCP Protocol Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
          <div>
            <p className="mb-2"><strong>1. Create Context:</strong> AI models create standardized context containers</p>
            <p className="mb-2"><strong>2. Set Priority:</strong> Contexts have priority levels (1-10) for importance</p>
            <p className="mb-2"><strong>3. Target Models:</strong> Specify which models should receive the context</p>
          </div>
          <div>
            <p className="mb-2"><strong>4. Share:</strong> Server broadcasts context to all relevant clients</p>
            <p className="mb-2"><strong>5. Sync:</strong> Clients can request sync to get latest contexts</p>
            <p className="mb-2"><strong>6. TTL:</strong> Contexts expire automatically after time-to-live</p>
          </div>
        </div>
      </div>

      {/* Context Types */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {['market_data', 'earning_history', 'wallet_balance', 'trade_signal', 'risk_profile', 'ml_prediction'].map((type) => (
          <div key={type} className="bg-white border border-gray-200 rounded-lg p-3 text-center">
            <ArrowRight className="w-5 h-5 text-gray-400 mx-auto mb-1" />
            <p className="text-sm font-medium text-gray-700">{type.replace(/_/g, ' ')}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MCP;
