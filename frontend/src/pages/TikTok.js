import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Video, 
  Cpu, 
  Play, 
  Pause, 
  RefreshCw, 
  Users, 
  Settings, 
  Sparkles, 
  Clock, 
  MessageSquare, 
  DollarSign, 
  TrendingUp, 
  ShieldAlert,
  ArrowRightRight,
  TrendingDown
} from 'lucide-react';

const TikTok = () => {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatus();
    // Poll status every 5 seconds when automation is running
    const interval = setInterval(() => {
      fetchStatus(true);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await axios.get('/api/tiktok/status');
      setState(res.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch TikTok status:', err);
      setError('Load failed');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const handleToggle = async () => {
    if (!state) return;
    setActionLoading(true);
    try {
      const res = await axios.post('/api/tiktok/toggle', { running: !state.is_running });
      setState(res.data);
      setError(null);
    } catch (err) {
      alert('Failed to toggle automation');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSimulateTick = async () => {
    setActionLoading(true);
    try {
      const res = await axios.post('/api/tiktok/simulate-tick');
      setState(res.data);
      setError(null);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to simulate tick');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Are you sure you want to reset TikTok automation metrics and logs?')) return;
    setActionLoading(true);
    try {
      const res = await axios.post('/api/tiktok/reset');
      setState(res.data);
      setError(null);
    } catch (err) {
      alert('Failed to reset automation state');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !state) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gray-900 text-white p-6 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-cyan-500/10 pointer-events-none" />
        <div className="relative z-10 space-y-1">
          <h1 className="text-3xl font-extrabold flex items-center gap-3 tracking-tight">
            <Video className="w-8 h-8 text-red-500 animate-pulse" />
            🤖 TikTok FULL AUTOMATION
          </h1>
          <p className="text-gray-400 text-sm md:text-base font-medium">
            Zero Manual Work Required — Complete Set & Forget System
          </p>
        </div>
        <div className="relative z-10 flex gap-3">
          <button
            onClick={handleToggle}
            disabled={actionLoading}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all shadow-lg active:scale-95 ${
              state?.is_running 
                ? 'bg-red-600 hover:bg-red-700 text-white shadow-red-500/20' 
                : 'bg-gradient-to-r from-red-500 to-cyan-500 hover:brightness-110 text-white shadow-purple-500/20'
            }`}
          >
            {state?.is_running ? (
              <>
                <Pause className="w-5 h-5 fill-current" />
                Stop Autopilot
              </>
            ) : (
              <>
                <Play className="w-5 h-5 fill-current" />
                One-Click Activation
              </>
            )}
          </button>
          
          <button
            onClick={handleSimulateTick}
            disabled={actionLoading || !state?.is_running}
            className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 px-4 py-3 rounded-xl font-bold transition-colors disabled:opacity-40"
            title="Simulate Auto posting cycle immediately"
          >
            <RefreshCw className={`w-5 h-5 ${actionLoading ? 'animate-spin' : ''}`} />
            Run Cycle
          </button>
          
          <button
            onClick={handleReset}
            disabled={actionLoading}
            className="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-400 hover:text-white rounded-xl transition-colors"
            title="Reset simulation data"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-950/40 border border-red-500/30 text-red-200 p-5 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-red-500/20 rounded-xl text-red-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">❌ Automation Error</h3>
            <p className="text-sm text-red-300">{error}. Check server status and connection.</p>
          </div>
        </div>
      )}

      {/* Stats Counter Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute right-4 top-4 p-2 bg-red-50 rounded-xl text-red-500">
            <Users className="w-6 h-6" />
          </div>
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-wider">Auto Accounts</p>
          <p className="text-4xl font-extrabold text-gray-900 mt-2">{state?.accounts_count || 0}</p>
          <div className="mt-3 text-xs text-red-600 font-bold flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-red-500 animate-ping inline-block" />
            Autopilot Running
          </div>
        </div>

        <div className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute right-4 top-4 p-2 bg-cyan-50 rounded-xl text-cyan-600">
            <Sparkles className="w-6 h-6" />
          </div>
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-wider">Content Generated</p>
          <p className="text-4xl font-extrabold text-gray-900 mt-2">{state?.content_generated || 0}</p>
          <div className="mt-3 text-xs text-gray-500 font-medium">AI Scripts & Videos</div>
        </div>

        <div className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute right-4 top-4 p-2 bg-green-50 rounded-xl text-green-600">
            <Video className="w-6 h-6" />
          </div>
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-wider">Auto Posted</p>
          <p className="text-4xl font-extrabold text-gray-900 mt-2">{state?.auto_posted || 0}</p>
          <div className="mt-3 text-xs text-gray-500 font-medium">Via Posting API</div>
        </div>

        <div className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute right-4 top-4 p-2 bg-purple-50 rounded-xl text-purple-600">
            <DollarSign className="w-6 h-6" />
          </div>
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-wider">Est. Revenue</p>
          <p className="text-4xl font-extrabold text-green-600 mt-2">€{state?.est_revenue?.toFixed(2) || '0.00'}</p>
          <div className="mt-3 text-xs text-green-600 font-bold">100% Passive Profit</div>
        </div>
      </div>

      {/* Main Grid: Auto Features & Live Stream Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Auto Features List */}
        <div className="lg:col-span-1 space-y-5 bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 pb-3 border-b">
            <Cpu className="w-5 h-5 text-gray-500" />
            🤖 AUTO-FEATURES (ZERO WORK):
          </h2>

          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="p-2 bg-red-50 text-red-500 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">📱</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Account Creation</h4>
                <p className="text-xs text-gray-500 mt-0.5">Creates multiple TikTok accounts automatically</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="p-2 bg-cyan-50 text-cyan-600 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">🎬</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Content Generation</h4>
                <p className="text-xs text-gray-500 mt-0.5">AI generates viral content, hooks, scripts automatically</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="p-2 bg-green-50 text-green-600 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">⏰</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Posting Schedule</h4>
                <p className="text-xs text-gray-500 mt-0.5">Posts 2-3 times per day at optimal times automatically</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="p-2 bg-orange-50 text-orange-500 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">💬</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Engagement</h4>
                <p className="text-xs text-gray-500 mt-0.5">Auto-likes, comments, follows for growth</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="p-2 bg-purple-50 text-purple-600 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">💰</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Monetization</h4>
                <p className="text-xs text-gray-500 mt-0.5">Sets up TikTok Shop, affiliate links, Creator Rewards</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg h-10 w-10 flex-shrink-0 flex items-center justify-center font-bold">📊</div>
              <div>
                <h4 className="font-bold text-gray-800 text-sm">Auto Optimization</h4>
                <p className="text-xs text-gray-500 mt-0.5">Analyzes performance and adjusts strategy automatically</p>
              </div>
            </div>
          </div>
        </div>

        {/* Live Stream Logs */}
        <div className="lg:col-span-2 space-y-4 bg-gray-900 text-gray-300 p-6 rounded-2xl border border-gray-800 shadow-inner flex flex-col h-[520px]">
          <div className="flex items-center justify-between pb-3 border-b border-gray-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-red-500 animate-pulse" />
              SYSTEM ACTIVITY LOGGER (LIVE STREAM)
            </h2>
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-gray-400 font-semibold uppercase">Autopilot Active</span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3.5 pr-2 font-mono text-xs scrollbar-thin scrollbar-thumb-gray-800">
            {state?.logs && state.logs.length > 0 ? (
              state.logs.map((log, idx) => (
                <div key={idx} className="flex items-start gap-2.5 leading-relaxed py-1 border-b border-gray-800/40 last:border-0">
                  <span className="text-gray-500 font-bold shrink-0">
                    [{new Date(log.timestamp).toLocaleTimeString()}]
                  </span>
                  
                  {log.type === 'success' && (
                    <span className="text-green-400 font-bold shrink-0">[SUCCESS]</span>
                  )}
                  {log.type === 'info' && (
                    <span className="text-cyan-400 font-bold shrink-0">[SYSTEM]</span>
                  )}
                  {log.type === 'money' && (
                    <span className="text-yellow-400 font-bold shrink-0">[PAYOUT]</span>
                  )}
                  {log.type === 'error' && (
                    <span className="text-red-400 font-bold shrink-0">[ERROR]</span>
                  )}

                  <span className={`${
                    log.type === 'money' ? 'text-yellow-200 font-bold' : 
                    log.type === 'success' ? 'text-green-100' : 'text-gray-300'
                  }`}>
                    {log.message}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-20 text-gray-500">
                No activity logs. Start autopilot to stream events.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default TikTok;
