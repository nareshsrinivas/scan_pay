import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CreditCard, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { ordersAPI, paymentsAPI } from '../services/api';

export default function Checkout() {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const orderUuid = searchParams.get('order');

  useEffect(() => {
    if (orderUuid) {
      loadOrder();
    } else {
      toast.error('No order found');
      navigate('/cart');
    }
  }, [orderUuid]);

  const loadOrder = async () => {
    try {
      const response = await ordersAPI.getById(orderUuid);
      setOrder(response.data);
    } catch (error) {
      toast.error('Order not found');
      navigate('/cart');
    }
  };

  const handlePayment = async () => {
    setLoading(true);
    try {
      // Step 1: Initiate payment
      toast.loading('Initiating payment...', { id: 'payment' });
      console.log('Initiating payment for order:', orderUuid);

      const response = await paymentsAPI.initiate(orderUuid, 'upi');
      console.log('Payment initiated:', response.data);

      // Step 2: Simulate payment processing
      toast.loading('Processing payment...', { id: 'payment' });
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 3: Send webhook to mark payment as successful
      console.log('Sending payment webhook...');
      const webhookResponse = await paymentsAPI.webhook({
        order_uuid: orderUuid,
        status: 'success',
        provider_reference: `txn_${Date.now()}`,
        transaction_id: `TXN-${Date.now()}`,
        amount: order.total_amount,
        payment_method: 'upi'
      });
      console.log('Webhook response:', webhookResponse.data);

      // Step 4: Wait for database to update
      await new Promise(resolve => setTimeout(resolve, 500));

      toast.success('Payment successful!', { id: 'payment' });

      // Step 5: Navigate to payment success page
      navigate(`/payment-success/${orderUuid}`);

    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.response?.data?.detail || 'Payment failed. Please try again.', { id: 'payment' });
      setLoading(false);
    }
  };

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/cart')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Cart
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Checkout</h1>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">Order Items</h2>
            <div className="space-y-3">
              {order.items && order.items.map((item) => (
                <div key={item.order_item_uuid} className="flex justify-between py-2 border-b">
                  <div>
                    <div className="font-semibold">{item.product_name}</div>
                    <div className="text-sm text-gray-600">Qty: {item.quantity}</div>
                  </div>
                  <div className="font-semibold">₹{item.subtotal}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">Payment Summary</h2>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{order.subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span>Taxes (GST)</span>
                <span>₹{order.tax_amount}</span>
              </div>
              <div className="border-t pt-3 flex justify-between font-bold text-xl">
                <span>Total Amount</span>
                <span className="text-primary">₹{order.total_amount}</span>
              </div>
            </div>

            <button
              onClick={handlePayment}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <CreditCard className="w-5 h-5" />
              <span>{loading ? 'Processing...' : 'Pay Now (UPI)'}</span>
            </button>

            <p className="text-xs text-gray-500 text-center mt-4">
              Demo Payment Mode - Auto-approved
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
