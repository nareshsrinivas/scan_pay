import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, ArrowLeft, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { QRCodeSVG } from 'qrcode.react';
import { exitQRAPI, ordersAPI } from '../services/api';

export default function ExitPass() {
  const { orderUuid } = useParams();
  const [exitQR, setExitQR] = useState(null);
  const [order, setOrder] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    loadExitQR();
    loadOrder();
  }, [orderUuid]);

  useEffect(() => {
    if (exitQR) {
      const expiresAt = new Date(exitQR.expires_at).getTime();
      const interval = setInterval(() => {
        const now = Date.now();
        const remaining = Math.max(0, Math.floor((expiresAt - now) / 1000));
        setTimeLeft(remaining);

        if (remaining === 0) {
          clearInterval(interval);
          toast.error('QR code expired');
        }
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [exitQR]);

  const loadExitQR = async () => {
    try {
      const response = await exitQRAPI.generate(orderUuid);
      setExitQR(response.data);
    } catch (error) {
      toast.error('Failed to load exit QR');
    }
  };

  const loadOrder = async () => {
    try {
      const response = await ordersAPI.getById(orderUuid);
      setOrder(response.data);
    } catch (error) {
      console.error('Failed to load order');
    }
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  if (!exitQR || !order) {
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
            Home
          </button>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-full mb-4">
              <CheckCircle2 className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Payment Successful</h1>
            <p className="text-gray-600">
              Use the code below to exit the store
            </p>
          </div>

          <div className="bg-white border-4 border-primary rounded-xl p-8 mb-6">
            <QRCodeSVG
              value={exitQR.token}
              size={256}
              level="H"
              className="mx-auto"
            />
          </div>

          <div className="bg-gradient-to-r from-primary/20 to-primary/10 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-700 mb-2">QR Code expires in</p>
            <div className="text-4xl font-bold text-primary">
              {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
            </div>
            <p className="text-xs text-gray-600 mt-1">Min : Sec</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold mb-2">Transaction Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Total Paid</span>
                <span className="font-bold">₹{order.total_amount}</span>
              </div>
              <div className="flex justify-between">
                <span>Transaction ID</span>
                <span className="font-mono">#{order.order_number}</span>
              </div>
              <div className="flex justify-between">
                <span>Payment Method</span>
                <span>UPI</span>
              </div>
            </div>
          </div>

          <button className="btn-secondary w-full flex items-center justify-center space-x-2">
            <Download className="w-5 h-5" />
            <span>Download Receipt</span>
          </button>

          <p className="text-xs text-gray-500 mt-4">
            Protected by encrypted exit verification. If you experience issues at the gate,
            please contact store staff or use the help button in the app.
          </p>
        </div>
      </div>
    </div>
  );
}
