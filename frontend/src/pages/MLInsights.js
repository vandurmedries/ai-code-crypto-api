import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Brain, TrendingUp, Activity, Target, Zap } from 'lucide-react';

const MLInsights = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [trends, setTrends] = useState([]);
  const [modelStats, setModelStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMLData();
  }, []);

  const fetchMLData = async () => {
    try {
      const [oppRes, predRes, trendsRes, statsRes] = await Promise.all([
        axios.get('/api/ml/opportunities'),
        axios.get('/api/ml/predict-earnings'),
        axios.get('/api/ml/market-trends'),
        axios.get('/api/ml/model-stats')
      ]);
      
      setOpportunities(oppRes.data);
      setPrediction(predRes.data);
      setTrends(trendsRes.data.trends);
      setModelStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch ML data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (strength) => {
    if (strength > 0.8) return <TrendingUp className="w-5 h-5 text-green-500" />;
    if (strength > 0.6) return <Activity className="w-5 h-5 text-blue-500" />;
    return <Target className="w-5 h-5 text-gray-500" />;
  };

  const getTrendColor = (direction) => {
    return direction === 'up' ? 'text-green-600' : 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Insights</h1>
        <p className="text-gray-600 mt-1">Machine learning powered market analysis and predictions</p>
      </div>

      {/* Model Stats */}
      {modelStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg shadow p-6 text-white">
            <p className="text-purple-200">Active Models</p>
            <p className="text-3xl font-bold">{modelStats.active_models}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg shadow p-6 text-white">
            <p className="text-blue-200">Total Predictions</p>
            <p className="text-3xl font-bold">{modelStats.total_predictions.toLocaleString()}</p>
          </div>
          <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg shadow p-6 text-white">
            <p className="text-green-200">Accuracy Rate</p>
            <p className="text-3xl font-bold">{(modelStats.accuracy_rate * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-gradient-to-br from-orange-600 to-orange-700 rounded-lg shadow p-6 text-white">
            <p className="text-orange-200">Avg Confidence</p>
            <p className="text-3xl font-bold">{(modelStats.avg_confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      )}

      {/* Earnings Prediction */}
      {prediction && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-purple-600" />
            <h2 className="text-lg font-semibold text-gray-900">AI Earnings Prediction</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Predicted Earning (30 days)</p>
              <p className="text-2xl font-bold text-purple-900">${prediction.predicted_earning.toFixed(2)}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">AI Confidence</p>
              <p className="text-2xl font-bold text-blue-900">{(prediction.confidence * 100).toFixed(0)}%</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Historical Average</p>
              <p className="text-2xl font-bold text-green-900">${prediction.factors.earning_history.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Earning Opportunities */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-yellow-500" />
            <h2 className="text-lg font-semibold text-gray-900">Active Earning Opportunities</h2>
          </div>
        </div>
        
        {opportunities.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {opportunities.map((opp) => (
              <div key={opp.opportunity_id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900 capitalize">{opp.type.replace(/_/g, ' ')}</h3>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                        {(opp.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm">{opp.description}</p>
                    <p className="text-sm text-blue-600 mt-2">{opp.action_required}</p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-xl font-bold text-green-600">+${opp.potential_earning.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">Potential</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-6 py-12 text-center text-gray-500">
            No active opportunities detected at this time
          </div>
        )}
      </div>

      {/* Market Trends */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900">Market Trend Analysis</h2>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {trends.map((trend, index) => (
            <div key={index} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getTrendIcon(trend.strength)}
                  <div>
                    <p className="font-medium text-gray-900 capitalize">{trend.type.replace(/_/g, ' ')}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-sm font-medium ${getTrendColor(trend.direction)}`}>
                        {trend.direction === 'up' ? '↗ Rising' : '→ Stable'}
                      </span>
                      <span className="text-sm text-gray-500">
                        Strength: {(trend.strength * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-900">
                    ×{trend.potential_multiplier.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">Multiplier</p>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${trend.strength * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MLInsights;
