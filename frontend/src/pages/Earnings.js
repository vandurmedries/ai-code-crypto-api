import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Wallet, RefreshCw, Sparkles } from 'lucide-react';

const Earnings = () => {
  const [earnings, setEarnings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triggerLoading, setTriggerLoading] = useState(false);

  useEffect(() => {
    fetchEarnings();
    fetchStats();
  }, []);

  const fetchEarnings = async () => {
    try {
      const response = await axios.get('/api/earnings/');
      setEarnings(response.data);
    } catch (error) {
      console.error('Failed to fetch earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/earnings/total');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const triggerAutoEarn = async () => {
    setTriggerLoading(true);
    try {
      const response = await axios.post('/api/ml/trigger-auto-earn');
      if (response.data.success) {
        alert(`Auto-earn successful! Earned $${response.data.earning.amount}`);
        fetchEarnings();
        fetchStats();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert('Failed to trigger auto-earn');
    } finally {
      setTriggerLoading(false);
    }
  };

  const getSourceColor = (source) => {
    const colors = {
      'ai_prediction': 'bg-purple-100 text-purple-800',
      'affiliate': 'bg-blue-100 text-blue-800',
      'data_analysis': 'bg-green-100 text-green-800',
      'market_trend': 'bg-orange-100 text-orange-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Earnings</h1>
          <p className="text-gray-600 mt-1">Track your AI-generated earnings</p>
        </div>
        <button
          onClick={triggerAutoEarn}
          disabled={triggerLoading}
          className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {triggerLoading ? 'Processing...' : 'Trigger Auto-Earn'}
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Total Earnings</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_count}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Total Amount</p>
            <p className="text-2xl font-bold text-green-600 mt-1">${stats.total_amount.toFixed(2)}</p>
          </div>
          {Object.entries(stats.by_source || {}).map(([source, amount]) => (
            <div key={source} className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 capitalize">{source.replace(/_/g, ' ')}</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">${amount.toFixed(2)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Earnings List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Earning History</h2>
        </div>
        
        {earnings.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {earnings.map((earning) => (
              <div key={earning.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-green-100 rounded-full">
                    <Wallet className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {earning.description || `Earning from ${earning.source}`}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getSourceColor(earning.source)}`}>
                        {earning.source}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(earning.created_at).toLocaleDateString()}
                      </span>
                      {earning.confidence_score && (
                        <span className="text-sm text-purple-600">
                          {(earning.confidence_score * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <span className="text-lg font-semibold text-green-600">+${earning.amount.toFixed(2)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-6 py-12 text-center">
            <Wallet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No earnings yet</p>
            <p className="text-sm text-gray-400 mt-1">AI will automatically generate earnings based on market opportunities</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Earnings;
