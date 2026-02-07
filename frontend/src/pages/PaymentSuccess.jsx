import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { exitQRAPI, ordersAPI } from '../services/api';

export default function PaymentSuccess() {
  const { orderUuid } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (orderUuid) {
      generateExitQR();
    }
  }, [orderUuid, retryCount]);

  const generateExitQR = async () => {
    try {
      setLoading(true);
      setError(null);

      // Wait a bit for order status to update in database
      await new Promise(resolve => setTimeout(resolve, 1500));

      console.log('Generating exit QR for order:', orderUuid);
      const response = await exitQRAPI.generate(orderUuid);

      if (response.data) {
        toast.success('Exit QR generated!');
        // Navigate to exit pass
        setTimeout(() => {
          navigate(`/exit-pass/${orderUuid}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Exit QR generation error:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to generate exit QR';
      setError(errorMsg);

      // If it's an order status issue, we can retry
      if (retryCount < 3 && errorMsg.includes('paid')) {
        toast.error(`Waiting for payment confirmation... (Retry ${retryCount + 1}/3)`);
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const handleManualNavigate = () => {
    navigate(`/exit-pass/${orderUuid}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="mb-6">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary/20 rounded-full mb-4">
            <CheckCircle2 className="w-12 h-12 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600">
            Your transaction has been verified.
          </p>
        </div>

        {loading ? (
          <div className="py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
            <p className="text-sm text-gray-600 mt-4">Generating exit QR code...</p>
            <p className="text-xs text-gray-400 mt-2">This may take a few seconds</p>
          </div>
        ) : error ? (
          <div className="py-4">
            <p className="text-red-600 mb-4">{error}</p>
            <div className="space-y-3">
              <button
                onClick={handleRetry}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-5 h-5" />
                Try Again
              </button>
              <button
                onClick={handleManualNavigate}
                className="btn-secondary w-full"
              >
                Continue Anyway
              </button>
            </div>
          </div>
        ) : (
          <div className="py-4">
            <p className="text-gray-700 mb-4">
              Exit QR generated! Redirecting...
            </p>
            <button
              onClick={handleManualNavigate}
              className="btn-primary w-full"
            >
              View Exit Pass
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
