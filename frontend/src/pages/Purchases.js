import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ShoppingCart, CheckCircle, CreditCard, Package } from 'lucide-react';

const Purchases = () => {
  const [products, setProducts] = useState({});
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchaseLoading, setPurchaseLoading] = useState(null);

  useEffect(() => {
    fetchProducts();
    fetchPurchases();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/purchases/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchPurchases = async () => {
    try {
      const response = await axios.get('/api/purchases/');
      setPurchases(response.data);
    } catch (error) {
      console.error('Failed to fetch purchases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (productId) => {
    setPurchaseLoading(productId);
    try {
      const response = await axios.post('/api/purchases/create', null, {
        params: { product_id: productId }
      });
      alert(`Successfully purchased ${response.data.purchase.product_name}!`);
      fetchPurchases();
    } catch (error) {
      alert(error.response?.data?.detail || 'Purchase failed');
    } finally {
      setPurchaseLoading(null);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'completed': 'bg-green-100 text-green-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Purchase AI Tools</h1>
        <p className="text-gray-600 mt-1">Use your earnings to purchase AI-powered tools</p>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(products).map(([id, product]) => (
          <div key={id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-100 rounded-full">
                  <Package className="w-6 h-6 text-blue-600" />
                </div>
                <span className="text-2xl font-bold text-gray-900">${product.price}</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
              <p className="text-gray-600 mt-2 text-sm">
                Premium AI tool for automated earning and market analysis.
              </p>
              <button
                onClick={() => handlePurchase(id)}
                disabled={purchaseLoading === id}
                className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <ShoppingCart className="w-4 h-4" />
                {purchaseLoading === id ? 'Processing...' : 'Purchase with Balance'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Purchase History */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Purchase History</h2>
        </div>
        
        {purchases.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {purchases.map((purchase) => (
              <div key={purchase.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-blue-100 rounded-full">
                    {purchase.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-blue-600" />
                    ) : (
                      <CreditCard className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{purchase.product_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 text-xs rounded-full capitalize ${getStatusColor(purchase.status)}`}>
                        {purchase.status}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(purchase.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                <span className="text-lg font-semibold text-orange-600">-${purchase.amount.toFixed(2)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-6 py-12 text-center">
            <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No purchases yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Purchases;
