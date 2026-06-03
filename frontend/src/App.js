import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Earnings from './pages/Earnings';
import Purchases from './pages/Purchases';
import MLInsights from './pages/MLInsights';
import Wallets from './pages/Wallets';
import A2A from './pages/A2A';
import MCP from './pages/MCP';
import Ruflo from './pages/Ruflo';
import Affiliate from './pages/Affiliate';
import TikTok from './pages/TikTok';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/earnings" element={<Earnings />} />
            <Route path="/purchases" element={<Purchases />} />
            <Route path="/ml-insights" element={<MLInsights />} />
            <Route path="/wallets" element={<Wallets />} />
            <Route path="/a2a" element={<A2A />} />
            <Route path="/mcp" element={<MCP />} />
<Route path="/ruflo" element={<Ruflo />} />
<Route path="/affiliate" element={<Affiliate />} />
<Route path="/tiktok" element={<TikTok />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
