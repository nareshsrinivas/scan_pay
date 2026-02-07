import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { cartAPI, ordersAPI } from '../services/api';

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const response = await cartAPI.get();
      setCart(response.data);
    } catch (error) {
      toast.error('Failed to load cart');
    }
  };

  const handleUpdateQuantity = async (cartUuid, newQuantity) => {
    try {
      const response = await cartAPI.update(cartUuid, newQuantity);
      setCart(response.data);
      toast.success('Cart updated');
    } catch (error) {
      toast.error('Failed to update');
    }
  };

  const handleRemove = async (cartUuid) => {
    try {
      await cartAPI.remove(cartUuid);
      loadCart();
      toast.success('Item removed');
    } catch (error) {
      toast.error('Failed to remove');
    }
  };

  const handleCheckout = async () => {
    setLoading(true);
    try {
      const response = await ordersAPI.create();
      const orderUuid = response.data.order_uuid;
      navigate(`/checkout?order=${orderUuid}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  if (!cart) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button onClick={() => navigate('/')} className="flex items-center text-gray-600">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Continue Shopping
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Your Cart</h1>

        {cart.items.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center">
            <p className="text-gray-500 text-lg">Your cart is empty</p>
            <button onClick={() => navigate('/')} className="btn-primary mt-4">
              Start Shopping
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-4">
              {cart.items.map((item) => (
                <div key={item.cart_uuid} className="bg-white rounded-xl p-4 flex items-center space-x-4">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg">{item.product_name}</h3>
                    <p className="text-sm text-gray-600">₹{item.product_price} each</p>
                    
                    <div className="flex items-center space-x-2 mt-2">
                      <button
                        onClick={() => handleUpdateQuantity(item.cart_uuid, item.quantity - 1)}
                        className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"
                      >
                        -
                      </button>
                      <span className="font-semibold">{item.quantity}</span>
                      <button
                        onClick={() => handleUpdateQuantity(item.cart_uuid, item.quantity + 1)}
                        className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xl font-bold text-primary">
                      ₹{item.subtotal}
                    </div>
                    <button
                      onClick={() => handleRemove(item.cart_uuid)}
                      className="mt-2 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="md:col-span-1">
              <div className="bg-white rounded-xl p-6 sticky top-4">
                <h2 className="text-xl font-bold mb-4">Order Summary</h2>
                
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span>₹{cart.subtotal}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Taxes (GST)</span>
                    <span>₹{cart.tax_amount}</span>
                  </div>
                  <div className="border-t pt-3 flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span className="text-primary">₹{cart.total_amount}</span>
                  </div>
                </div>

                <button
                  onClick={handleCheckout}
                  disabled={loading}
                  className="btn-primary w-full"
                >
                  {loading ? 'Processing...' : 'Proceed to Checkout'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
