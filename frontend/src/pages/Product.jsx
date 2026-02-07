import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Minus } from 'lucide-react';
import toast from 'react-hot-toast';
import { productsAPI, cartAPI } from '../services/api';

export default function Product() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProduct();
  }, [uuid]);

  const loadProduct = async () => {
    try {
      const response = await productsAPI.getByQR(uuid);
      setProduct(response.data);
    } catch (error) {
      toast.error('Product not found');
      navigate('/');
    }
  };

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      await cartAPI.add(product.product_uuid, quantity);
      toast.success(`Added ${quantity} item(s) to cart`);
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
    } finally {
      setLoading(false);
    }
  };

  if (!product) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button onClick={() => navigate(-1)} className="flex items-center text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="md:flex">
            <div className="md:w-1/2 bg-gray-100 flex items-center justify-center p-8">
              <img
                src={product.image_url || 'https://via.placeholder.com/400'}
                alt={product.name}
                className="max-h-96 object-contain"
              />
            </div>

            <div className="md:w-1/2 p-8">
              <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
              <p className="text-gray-600 mb-4">SKU: {product.sku}</p>
              
              <div className="text-4xl font-bold text-primary mb-6">
                ₹{product.price}
              </div>

              {product.description && (
                <p className="text-gray-700 mb-6">{product.description}</p>
              )}

              <div className="flex items-center space-x-4 mb-6">
                <span className="font-medium">Quantity:</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    <Minus className="w-5 h-5" />
                  </button>
                  <span className="w-12 text-center font-bold">{quantity}</span>
                  <button
                    onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                    className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="text-sm text-gray-600 mb-6">
                {product.stock > 0 ? (
                  <span className="text-green-600">In Stock ({product.stock} available)</span>
                ) : (
                  <span className="text-red-600">Out of Stock</span>
                )}
              </div>

              <button
                onClick={handleAddToCart}
                disabled={loading || product.stock === 0}
                className="btn-primary w-full"
              >
                {loading ? 'Adding...' : 'Add to Cart'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
