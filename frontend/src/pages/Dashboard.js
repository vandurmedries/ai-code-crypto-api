import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { 
  Wallet, 
  TrendingUp, 
  ShoppingCart, 
  Sparkles,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get('/api/users/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const StatCard = ({ title, value, icon: Icon, trend, color }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">${value.toFixed(2)}</p>
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="flex items-center mt-4 text-sm">
          {trend > 0 ? (
            <>
              <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600 font-medium">+{trend}%</span>
            </>
          ) : (
            <>
              <ArrowDownRight className="w-4 h-4 text-red-500 mr-1" />
              <span className="text-red-600 font-medium">{trend}%</span>
            </>
          )}
          <span className="text-gray-500 ml-2">from last month</span>
        </div>
      )}
    </div>
  );

  const chartData = [
    { name: 'Week 1', earnings: 120, purchases: 50 },
    { name: 'Week 2', earnings: 200, purchases: 80 },
    { name: 'Week 3', earnings: 150, purchases: 30 },
    { name: 'Week 4', earnings: 280, purchases: 120 },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back, {user?.full_name || user?.email}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Current Balance"
          value={stats?.balance || 0}
          icon={Wallet}
          trend={12.5}
          color="bg-blue-600"
        />
        <StatCard
          title="Total Earned"
          value={stats?.total_earned || 0}
          icon={TrendingUp}
          trend={8.2}
          color="bg-green-600"
        />
        <StatCard
          title="Total Spent"
          value={stats?.total_spent || 0}
          icon={ShoppingCart}
          trend={-3.1}
          color="bg-orange-600"
        />
        <StatCard
          title="AI Opportunities"
          value={stats?.active_opportunities?.length || 0}
          icon={Sparkles}
          color="bg-purple-600"
        />
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Earnings vs Purchases</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="earnings" stroke="#10b981" strokeWidth={2} name="Earnings" />
              <Line type="monotone" dataKey="purchases" stroke="#f97316" strokeWidth={2} name="Purchases" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Active Opportunities */}
      {stats?.active_opportunities && stats.active_opportunities.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">AI-Detected Earning Opportunities</h2>
          <div className="space-y-4">
            {stats.active_opportunities.map((opp) => (
              <div key={opp.opportunity_id} className="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600" />
                    <h3 className="font-medium text-gray-900 capitalize">{opp.type.replace(/_/g, ' ')}</h3>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      {(opp.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{opp.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-green-600">+${opp.potential_earning.toFixed(2)}</p>
                  <p className="text-xs text-gray-500">Potential</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Earnings</h2>
          {stats?.recent_earnings?.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_earnings.map((earning) => (
                <div key={earning.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{earning.source}</p>
                    <p className="text-sm text-gray-500">{new Date(earning.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className="font-semibold text-green-600">+${earning.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No recent earnings</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Purchases</h2>
          {stats?.recent_purchases?.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_purchases.map((purchase) => (
                <div key={purchase.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{purchase.product_name}</p>
                    <p className="text-sm text-gray-500">{new Date(purchase.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className="font-semibold text-orange-600">-${purchase.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No recent purchases</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
