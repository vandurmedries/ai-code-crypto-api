import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Wallet, ArrowDownCircle, ArrowUpCircle, PlusCircle, Bitcoin, Activity } from 'lucide-react';

const Wallets = () => {
  const [wallets, setWallets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCurrency, setNewCurrency] = useState('BTC');

  useEffect(() => {
    fetchWallets();
  }, []);

  const fetchWallets = async () => {
    try {
      const response = await axios.get('/api/wallets/');
      setWallets(response.data);
      
      // Fetch transactions for first wallet if exists
      if (response.data.length > 0) {
        fetchTransactions(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch wallets:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async (walletId) => {
    try {
      const response = await axios.get(`/api/wallets/${walletId}/transactions`);
      setTransactions(response.data.transactions || []);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
  };

  const createWallet = async () => {
    try {
      await axios.post(`/api/wallets/create?currency=${newCurrency}&network=mainnet`);
      fetchWallets();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to create wallet');
    }
  };

  const simulateDeposit = async (walletId) => {
    try {
      const response = await axios.post(`/api/wallets/simulate-deposit?wallet_id=${walletId}&amount=0.5`);
      alert(`Deposited 0.5 BTC! New balance: ${response.data.new_balance}`);
      fetchWallets();
    } catch (error) {
      alert('Deposit failed');
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
            <Wallet className="w-8 h-8 text-orange-500" />
            Crypto Wallets
          </h1>
          <p className="text-gray-600 mt-1">Manage your blockchain wallets (BTC, ETH, SOL, USDT)</p>
        </div>
        <div className="flex gap-2">
          <select 
            value={newCurrency} 
            onChange={(e) => setNewCurrency(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
            <option value="SOL">Solana (SOL)</option>
            <option value="USDT">Tether (USDT)</option>
          </select>
          <button 
            onClick={createWallet}
            className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
          >
            <PlusCircle className="w-5 h-5" />
            Create Wallet
          </button>
        </div>
      </div>

      {/* Wallets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {wallets.map((wallet) => (
          <div key={wallet.id} className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-orange-100 rounded-full">
                  <Bitcoin className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{wallet.currency}</h3>
                  <p className="text-sm text-gray-500">{wallet.network}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${wallet.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {wallet.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600">Balance</p>
              <p className="text-2xl font-bold text-gray-900">{wallet.balance.toFixed(8)} {wallet.currency}</p>
              {wallet.pending_balance > 0 && (
                <p className="text-sm text-yellow-600">Pending: {wallet.pending_balance.toFixed(8)}</p>
              )}
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-1">Address</p>
              <p className="text-xs font-mono text-gray-500 break-all">{wallet.address}</p>
            </div>
            
            <div className="flex gap-2">
              <button 
                onClick={() => simulateDeposit(wallet.id)}
                className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 text-sm"
              >
                <ArrowDownCircle className="w-4 h-4" />
                Deposit
              </button>
              <button 
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 text-sm opacity-50 cursor-not-allowed"
                disabled
              >
                <ArrowUpCircle className="w-4 h-4" />
                Withdraw
              </button>
            </div>
          </div>
        ))}
        
        {wallets.length === 0 && (
          <div className="col-span-full bg-gray-50 rounded-lg p-12 text-center">
            <Wallet className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No wallets yet</p>
            <p className="text-sm text-gray-400 mt-1">Create your first crypto wallet above</p>
          </div>
        )}
      </div>

      {/* Transactions */}
      {transactions.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Recent Transactions
            </h2>
          </div>
          <div className="divide-y divide-gray-200">
            {transactions.map((tx) => (
              <div key={tx.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-full ${tx.tx_type === 'deposit' ? 'bg-green-100' : 'bg-orange-100'}`}>
                    {tx.tx_type === 'deposit' ? 
                      <ArrowDownCircle className="w-5 h-5 text-green-600" /> : 
                      <ArrowUpCircle className="w-5 h-5 text-orange-600" />
                    }
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 capitalize">{tx.tx_type}</p>
                    <p className="text-sm text-gray-500">
                      {tx.tx_hash ? `${tx.tx_hash.slice(0, 8)}...${tx.tx_hash.slice(-8)}` : 'Pending'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{tx.amount.toFixed(8)} {tx.currency}</p>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    tx.status === 'confirmed' ? 'bg-green-100 text-green-800' : 
                    tx.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800'
                  }`}>
                    {tx.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Wallets;
