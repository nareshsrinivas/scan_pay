import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { exitQRAPI } from '../services/api';

export default function PaymentSuccess() {
  const { orderUuid } = useParams();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    generateExitQR();
  }, [orderUuid]);

  const generateExitQR = async () => {
    try {
      await exitQRAPI.generate(orderUuid);
      setLoading(false);
      setTimeout(() => {
        navigate(`/exit-pass/${orderUuid}`);
      }, 3000);
    } catch (error) {
      toast.error('Failed to generate exit QR');
      setLoading(false);
    }
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
          </div>
        ) : (
          <div className="py-4">
            <p className="text-gray-700">
              Use the code below to exit the store.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
