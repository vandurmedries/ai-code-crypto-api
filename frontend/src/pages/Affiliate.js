import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, TrendingUp, Share2, Target, Zap, Globe, BarChart3, Play, Pause, Award } from 'lucide-react';

const Affiliate = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoRunning, setAutoRunning] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [campaignsRes, statsRes, oppRes] = await Promise.all([
        axios.get('/api/affiliate/campaigns'),
        axios.get('/api/affiliate/stats'),
        axios.get('/api/affiliate/opportunities')
      ]);
      setCampaigns(campaignsRes.data.campaigns || []);
      setStats(statsRes.data);
      setOpportunities(oppRes.data.opportunities || []);
    } catch (error) {
      console.error('Affiliate fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const createCampaign = async () => {
    try {
      await axios.post('/api/affiliate/campaigns/create?method=affiliate_marketing');
      fetchData();
    } catch (error) {
      alert('Failed to create campaign');
    }
  };

  const executeCampaign = async (campaignId) => {
    try {
      const res = await axios.post(`/api/affiliate/campaigns/${campaignId}/execute`);
      alert(`Campaign executed! Posts: ${res.data.posts_created}, Potential: $${res.data.potential_earnings}`);
      fetchData();
    } catch (error) {
      alert('Execution failed');
    }
  };

  const simulateDay = async (campaignId) => {
    try {
      const res = await axios.post(`/api/affiliate/campaigns/${campaignId}/simulate-day`);
      alert(`Daily earnings: $${res.data.daily_earnings}`);
      fetchData();
    } catch (error) {
      alert('Simulation failed');
    }
  };

  const startAutoRun = async () => {
    try {
      setAutoRunning(true);
      const res = await axios.post('/api/affiliate/auto-run');
      alert(`Autonomous mode activated! Immediate earnings: $${res.data.immediate_earnings}`);
      fetchData();
    } catch (error) {
      alert('Auto-run failed');
      setAutoRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <DollarSign className="w-8 h-8 text-green-500" />
            Autonomous Earning
          </h1>
          <p className="text-gray-600 mt-1">Real money through affiliate marketing - fully automated</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={startAutoRun}
            disabled={autoRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${autoRunning ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'} text-white`}
          >
            <Zap className="w-5 h-5" />
            {autoRunning ? 'Running...' : 'Start Auto-Earn'}
          </button>
          <button 
            onClick={createCampaign}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Target className="w-5 h-5" />
            New Campaign
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
            <p className="text-green-100 text-sm">Total Earned</p>
            <p className="text-3xl font-bold">${stats.total_earned.toFixed(2)}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
            <p className="text-blue-100 text-sm">Campaigns</p>
            <p className="text-3xl font-bold">{stats.total_campaigns}</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-4 text-white">
            <p className="text-purple-100 text-sm">Conversions</p>
            <p className="text-3xl font-bold">{stats.total_conversions}</p>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow p-4 text-white">
            <p className="text-orange-100 text-sm">Conv. Rate</p>
            <p className="text-3xl font-bold">{stats.conversion_rate}%</p>
          </div>
        </div>
      )}

      {/* How it Works */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5 text-green-600" />
          How Autonomous Earning Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-green-600 font-bold mb-1">1. Discover</div>
            <p className="text-gray-600">AI finds trending products with high commissions</p>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-blue-600 font-bold mb-1">2. Create Content</div>
            <p className="text-gray-600">Auto-generates posts, reviews, and affiliate links</p>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-purple-600 font-bold mb-1">3. Distribute</div>
            <p className="text-gray-600">Posts to social media, blogs, and forums</p>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-orange-600 font-bold mb-1">4. Earn</div>
            <p className="text-gray-600">Commissions flow in when people buy</p>
          </div>
        </div>
      </div>

      {/* Active Campaigns */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Active Campaigns ({campaigns.length})
        </h2>
        <div className="space-y-3">
          {campaigns.map((campaign) => (
            <div key={campaign.campaign_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-100 rounded-full">
                  <DollarSign className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{campaign.method}</p>
                  <p className="text-sm text-gray-500">ID: {campaign.campaign_id.slice(0,8)}</p>
                  <p className="text-xs text-gray-400">Posts: {campaign.total_posts} | Clicks: {campaign.total_clicks}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="font-semibold text-green-600">${campaign.total_earned.toFixed(2)}</p>
                  <span className={`px-2 py-1 text-xs rounded-full ${campaign.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {campaign.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => executeCampaign(campaign.campaign_id)}
                    className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    <Play className="w-4 h-4" />
                    Run
                  </button>
                  <button 
                    onClick={() => simulateDay(campaign.campaign_id)}
                    className="flex items-center gap-1 bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Day
                  </button>
                </div>
              </div>
            </div>
          ))}
          {campaigns.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p>No campaigns yet</p>
              <p className="text-sm mt-1">Click "New Campaign" to start earning</p>
            </div>
          )}
        </div>
      </div>

      {/* Trending Opportunities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-orange-500" />
          Trending Opportunities ({opportunities.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {opportunities.slice(0, 4).map((opp) => (
            <div key={opp.opportunity_id} className="border border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{opp.name}</h3>
                  <p className="text-sm text-gray-500">{opp.category} • {opp.platform}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${opp.competition === 'low' ? 'bg-green-100 text-green-700' : opp.competition === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                  {opp.competition}
                </span>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <p className="text-gray-400 text-xs">Price</p>
                  <p className="font-medium">${opp.price}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Commission</p>
                  <p className="font-medium text-green-600">{(opp.commission_rate * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Monthly</p>
                  <p className="font-medium text-blue-600">${opp.estimated_monthly_earnings}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Earning Methods */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { name: 'Affiliate Marketing', icon: Share2, desc: 'Promote products', color: 'blue' },
          { name: 'Content Arbitrage', icon: Award, desc: 'Repurpose content', color: 'purple' },
          { name: 'Airdrop Hunting', icon: Target, desc: 'Free crypto', color: 'orange' },
          { name: 'Trend Trading', icon: TrendingUp, desc: 'Ride trends', color: 'green' }
        ].map((method) => (
          <div key={method.name} className={`bg-${method.color}-50 border border-${method.color}-200 rounded-lg p-4`}>
            <method.icon className={`w-8 h-8 text-${method.color}-600 mb-2`} />
            <h3 className="font-semibold text-gray-900">{method.name}</h3>
            <p className="text-sm text-gray-600">{method.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Affiliate;
