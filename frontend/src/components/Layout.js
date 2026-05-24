import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  Wallet, 
  ShoppingCart, 
  Brain,
  Bitcoin,
  Radio,
  Share2,
  Waves,
  DollarSign
} from 'lucide-react';

const Layout = () => {
  const { user } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/earnings', label: 'Earnings', icon: Wallet },
    { path: '/purchases', label: 'Purchases', icon: ShoppingCart },
    { path: '/ml-insights', label: 'AI Insights', icon: Brain },
    { path: '/wallets', label: 'Wallets', icon: Bitcoin },
    { path: '/a2a', label: 'A2A Network', icon: Radio },
    { path: '/mcp', label: 'MCP Protocol', icon: Share2 },
    { path: '/ruflo', label: 'Ruflo', icon: Waves },
    { path: '/affiliate', label: 'Autonomous Earn', icon: DollarSign },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex-shrink-0">
        <div className="p-6">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-400" />
            AI Earning
          </h1>
        </div>
        
        <nav className="mt-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-6 py-3 transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        
        <div className="mt-auto p-6 border-t border-gray-800">
          <div>
            <p className="text-sm text-gray-400">Auto User</p>
            <p className="font-medium">{user?.email || 'demo@local.ai'}</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
