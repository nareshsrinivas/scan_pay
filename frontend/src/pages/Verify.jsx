import { useState, useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { exitQRAPI } from '../services/api';

export default function Verify() {
  const [verificationResult, setVerificationResult] = useState(null);
  const [scanning, setScanning] = useState(true);

  useEffect(() => {
    initializeScanner();
    return () => cleanupScanner();
  }, []);

  const initializeScanner = () => {
    const scanner = new Html5QrcodeScanner('qr-scanner', {
      fps: 10,
      qrbox: { width: 300, height: 300 },
    });

    scanner.render(onScanSuccess, onScanError);
  };

  const cleanupScanner = () => {
    try {
      Html5QrcodeScanner.clear('qr-scanner');
    } catch (error) {}
  };

  const onScanSuccess = async (decodedText) => {
    setScanning(false);
    try {
      const response = await exitQRAPI.verify(decodedText);
      setVerificationResult(response.data);
      
      if (response.data.valid) {
        toast.success('Authorization successful!');
      } else {
        toast.error(response.data.message);
      }

      setTimeout(() => {
        setVerificationResult(null);
        setScanning(true);
        initializeScanner();
      }, 5000);
    } catch (error) {
      toast.error('Verification failed');
      setScanning(true);
    }
  };

  const onScanError = () => {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 to-green-700">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-3 bg-white/10 backdrop-blur px-6 py-3 rounded-full mb-4">
            <div className="w-3 h-3 bg-primary rounded-full animate-pulse" />
            <span className="text-white font-semibold">Exit Gate Control</span>
          </div>
          <h1 className="text-4xl font-bold text-white">Scan to Exit</h1>
          <p className="text-white/80 mt-2">
            Please align your Exit QR code with the scanner
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          {scanning && !verificationResult && (
            <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
              <div id="qr-scanner" className="w-full" />
            </div>
          )}

          {verificationResult && (
            <div className={`bg-white rounded-2xl shadow-2xl p-8 text-center ${
              verificationResult.valid 
                ? 'border-8 border-green-500' 
                : 'border-8 border-red-500'
            }`}>
              {verificationResult.valid ? (
                <>
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-green-500 rounded-full mb-4">
                      <CheckCircle className="w-16 h-16 text-white" />
                    </div>
                    <h2 className="text-4xl font-bold text-green-600 mb-2">
                      AUTHORIZED
                    </h2>
                    <p className="text-xl text-gray-700">
                      Customer can exit the store
                    </p>
                  </div>

                  <div className="bg-green-50 rounded-xl p-6 mb-6">
                    <div className="grid grid-cols-2 gap-4 text-left">
                      <div>
                        <p className="text-sm text-gray-600">Customer Name</p>
                        <p className="font-bold text-lg">{verificationResult.user_name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Order #</p>
                        <p className="font-bold text-lg">{verificationResult.order_number}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Items</p>
                        <p className="font-bold text-lg">{verificationResult.items_count}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Amount Paid</p>
                        <p className="font-bold text-lg text-green-600">
                          ₹{verificationResult.total_amount}
                        </p>
                      </div>
                    </div>
                  </div>

                  {verificationResult.items && (
                    <div className="bg-gray-50 rounded-xl p-4">
                      <p className="font-semibold mb-2">Order Summary</p>
                      <div className="space-y-1 text-sm">
                        {verificationResult.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between">
                            <span>{item.product_name} x{item.quantity}</span>
                            <span>₹{item.price * item.quantity}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-red-500 rounded-full mb-4">
                      {verificationResult.status === 'expired' ? (
                        <AlertCircle className="w-16 h-16 text-white" />
                      ) : (
                        <XCircle className="w-16 h-16 text-white" />
                      )}
                    </div>
                    <h2 className="text-4xl font-bold text-red-600 mb-2">
                      {verificationResult.status === 'expired' ? 'EXPIRED' : 'DENIED'}
                    </h2>
                    <p className="text-xl text-gray-700">
                      {verificationResult.message}
                    </p>
                  </div>

                  <div className="bg-red-50 rounded-xl p-6">
                    <p className="text-gray-700">
                      {verificationResult.status === 'expired' 
                        ? 'This QR code has expired. Please generate a new one.'
                        : verificationResult.status === 'already_used'
                        ? 'This QR code has already been used.'
                        : 'Invalid QR code. Please contact staff for assistance.'}
                    </p>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-6 bg-white/10 backdrop-blur px-6 py-3 rounded-full text-white text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span>System Online</span>
            </div>
            <div className="w-px h-4 bg-white/30" />
            <span>v2.4.1-stable</span>
            <div className="w-px h-4 bg-white/30" />
            <span>Latency: 42ms</span>
          </div>
        </div>
      </div>
    </div>
  );
}
