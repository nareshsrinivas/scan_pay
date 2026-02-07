import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { ShoppingBag, Zap, User } from 'lucide-react';
import toast from 'react-hot-toast';
import { cartAPI } from '../services/api';
import { useCartStore, useAuthStore } from '../store';

export default function Scan() {
  const [scanning, setScanning] = useState(false);
  const [scannedItems, setScannedItems] = useState(0);
  const navigate = useNavigate();
  const { cart, setCart } = useCartStore();
  const { user, logout } = useAuthStore();

  useEffect(() => {
    loadCart();
    initializeScanner();
    return () => cleanupScanner();
  }, []);

  const loadCart = async () => {
    try {
      const response = await cartAPI.get();
      setCart(response.data);
      setScannedItems(response.data.total_items || 0);
    } catch (error) {
      console.error('Failed to load cart');
    }
  };

  const initializeScanner = () => {
    const scanner = new Html5QrcodeScanner('qr-reader', {
      fps: 10,
      qrbox: { width: 250, height: 250 },
    });

    scanner.render(onScanSuccess, onScanError);
    setScanning(true);
  };

  const cleanupScanner = () => {
    try {
      Html5QrcodeScanner.clear('qr-reader');
    } catch (error) {}
  };

  const onScanSuccess = async (decodedText) => {
    try {
      if (decodedText.startsWith('PRODUCT:')) {
        const qrCode = decodedText;
        navigate(`/product/${qrCode}`);
      } else {
        toast.error('Invalid QR code');
      }
    } catch (error) {
      toast.error('Failed to scan product');
    }
  };

  const onScanError = () => {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Zap className="w-6 h-6" />
              <h1 className="text-xl font-bold">Express Checkout</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/cart')}
                className="relative p-2 hover:bg-gray-100 rounded-full"
              >
                <ShoppingBag className="w-6 h-6" />
                {scannedItems > 0 && (
                  <span className="absolute -top-1 -right-1 bg-primary text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                    {scannedItems}
                  </span>
                )}
              </button>
              <button
                onClick={logout}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <User className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Scanner Section */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-2xl font-bold mb-2">Scan Product</h2>
            <p className="text-gray-600 mb-6">
              Align the barcode or QR code within the frame
            </p>

            <div className="relative">
              <div
                id="qr-reader"
                className="rounded-lg overflow-hidden border-4 border-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-primary rounded-full" />
                  <span className="text-sm font-medium">Scanner Ready</span>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <span className="text-2xl font-bold text-primary">
                  {scannedItems} Items
                </span>
              </div>
            </div>
          </div>

          {/* Cart Preview */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-4">Your Shopping Cart</h2>

            {cart && cart.items.length > 0 ? (
              <div className="space-y-4">
                {cart.items.map((item) => (
                  <div
                    key={item.cart_uuid}
                    className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <h3 className="font-semibold">{item.product_name}</h3>
                      <p className="text-sm text-gray-600">
                        ₹{item.product_price} × {item.quantity}
                      </p>
                    </div>
                    <div className="text-primary font-bold">
                      ₹{item.subtotal}
                    </div>
                  </div>
                ))}

                <div className="border-t pt-4 mt-4">
                  <div className="flex justify-between mb-2">
                    <span>Subtotal</span>
                    <span>₹{cart.subtotal}</span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span>Taxes (GST)</span>
                    <span>₹{cart.tax_amount}</span>
                  </div>
                  <div className="flex justify-between font-bold text-lg border-t pt-2">
                    <span>Total Amount</span>
                    <span className="text-primary">₹{cart.total_amount}</span>
                  </div>
                </div>

                <button
                  onClick={() => navigate('/cart')}
                  className="btn-primary w-full mt-4"
                >
                  Proceed to Payment
                </button>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <ShoppingBag className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Your cart is empty</p>
                <p className="text-sm">Scan products to add them</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
