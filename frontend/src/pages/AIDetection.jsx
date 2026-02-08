import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, CheckCircle, XCircle, AlertCircle, ArrowLeft, Zap, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { aiAPI } from '../services/api';
import { useAuthStore } from '../store';

export default function AIDetection() {
    const [capturedImage, setCapturedImage] = useState(null);
    const [isDetecting, setIsDetecting] = useState(false);
    const [detectionResult, setDetectionResult] = useState(null);
    const [cameraActive, setCameraActive] = useState(false);
    const [expectedProducts, setExpectedProducts] = useState('');
    const [orderUuid, setOrderUuid] = useState('');
    const [cameraReady, setCameraReady] = useState(false);

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);
    const streamRef = useRef(null);
    const navigate = useNavigate();
    const { user } = useAuthStore();

    // Effect to attach stream to video element when camera becomes active
    useEffect(() => {
        if (cameraActive && videoRef.current && streamRef.current) {
            console.log('Attaching stream to video element');
            const video = videoRef.current;
            video.srcObject = streamRef.current;

            video.onloadedmetadata = () => {
                console.log('Video metadata loaded, dimensions:', video.videoWidth, 'x', video.videoHeight);
                video.play()
                    .then(() => {
                        console.log('Video playing successfully');
                        setCameraReady(true);
                        toast.success('Camera ready! Click Capture to take a photo');
                    })
                    .catch(err => {
                        console.error('Video play error:', err);
                        toast.error('Failed to play video: ' + err.message);
                    });
            };
        }
    }, [cameraActive]);

    const startCamera = async () => {
        console.log('Starting camera...');
        setCameraReady(false);

        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                toast.error('Camera not supported in this browser');
                return;
            }

            toast.loading('Opening camera...', { id: 'camera' });

            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } }
            });

            console.log('Camera stream obtained');
            streamRef.current = stream;

            // Set camera active AFTER we have the stream
            // The useEffect will handle attaching it to the video element
            setCameraActive(true);
            toast.dismiss('camera');

        } catch (error) {
            console.error('Camera error:', error);
            toast.dismiss('camera');

            if (error.name === 'NotAllowedError') {
                toast.error('Camera access denied. Please allow camera permission.');
            } else if (error.name === 'NotFoundError') {
                toast.error('No camera found on this device');
            } else {
                toast.error('Failed to open camera: ' + error.message);
            }
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setCameraActive(false);
    };

    const captureFromCamera = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            setCapturedImage(imageData);
            stopCamera();
        }
    };

    const handleFileUpload = (event) => {
        console.log('File upload triggered', event);
        const file = event.target.files[0];
        console.log('Selected file:', file);
        if (file) {
            toast.success('Loading image...');
            const reader = new FileReader();
            reader.onload = (e) => {
                console.log('File loaded successfully');
                setCapturedImage(e.target.result);
                toast.success('Image loaded! Now click Detect Products');
            };
            reader.onerror = (e) => {
                console.error('File read error:', e);
                toast.error('Failed to load image');
            };
            reader.readAsDataURL(file);
        } else {
            console.log('No file selected');
        }
    };

    const detectProducts = async () => {
        if (!capturedImage) {
            toast.error('Please capture or upload an image first');
            return;
        }

        setIsDetecting(true);
        setDetectionResult(null);

        try {
            // Extract base64 data (remove data:image/jpeg;base64, prefix)
            const base64Data = capturedImage.split(',')[1];
            const productsArray = expectedProducts
                .split(',')
                .map(p => p.trim())
                .filter(p => p.length > 0);

            const response = await aiAPI.detectProducts(
                base64Data,
                orderUuid || 'demo-order',
                productsArray
            );

            setDetectionResult(response.data);
            if (response.data.success) {
                toast.success('Detection completed!');
            }
        } catch (error) {
            console.error('Detection error:', error);
            toast.error('Detection failed');
            setDetectionResult({
                success: false,
                match_status: 'error',
                detected_products: [],
                missing_products: [],
                extra_products: [],
                confidence_score: 0
            });
        } finally {
            setIsDetecting(false);
        }
    };

    const resetDetection = () => {
        setCapturedImage(null);
        setDetectionResult(null);
        setExpectedProducts('');
        setOrderUuid('');
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'matched': return 'text-green-600 bg-green-50';
            case 'extra_items': return 'text-yellow-600 bg-yellow-50';
            case 'missing_items': return 'text-orange-600 bg-orange-50';
            case 'mismatch': return 'text-red-600 bg-red-50';
            default: return 'text-gray-600 bg-gray-50';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'matched': return <CheckCircle className="w-8 h-8 text-green-500" />;
            case 'extra_items': return <AlertCircle className="w-8 h-8 text-yellow-500" />;
            case 'missing_items': return <AlertCircle className="w-8 h-8 text-orange-500" />;
            case 'mismatch': return <XCircle className="w-8 h-8 text-red-500" />;
            default: return <AlertCircle className="w-8 h-8 text-gray-500" />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <button onClick={() => navigate('/')} className="p-2 hover:bg-gray-100 rounded-full">
                                <ArrowLeft className="w-5 h-5" />
                            </button>
                            <Zap className="w-6 h-6 text-primary" />
                            <h1 className="text-xl font-bold">AI Product Detection</h1>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid md:grid-cols-2 gap-8">
                    {/* Image Capture Section */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="text-xl font-bold mb-4">Capture Image</h2>

                        {!capturedImage ? (
                            <div className="space-y-4">
                                {cameraActive ? (
                                    <div className="relative">
                                        <video
                                            ref={videoRef}
                                            autoPlay
                                            playsInline
                                            muted
                                            className="w-full rounded-lg border-4 border-primary"
                                            style={{ minHeight: '300px', backgroundColor: '#000' }}
                                        />
                                        <button
                                            onClick={captureFromCamera}
                                            className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-primary text-white px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-primary-dark transition-colors"
                                        >
                                            <Camera className="w-5 h-5 inline mr-2" />
                                            Capture
                                        </button>
                                    </div>
                                ) : (
                                    <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center">
                                        <Camera className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                                        <p className="text-gray-600 mb-6">Capture or upload an image of products</p>

                                        <div className="flex flex-col sm:flex-row gap-3 justify-center">
                                            <button
                                                onClick={startCamera}
                                                className="btn-primary flex items-center justify-center space-x-2"
                                            >
                                                <Camera className="w-5 h-5" />
                                                <span>Open Camera</span>
                                            </button>
                                            <button
                                                onClick={() => fileInputRef.current?.click()}
                                                className="btn-secondary flex items-center justify-center space-x-2"
                                            >
                                                <Upload className="w-5 h-5" />
                                                <span>Upload Image</span>
                                            </button>
                                        </div>
                                    </div>
                                )}

                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                />

                                {cameraActive && (
                                    <button
                                        onClick={stopCamera}
                                        className="w-full btn-secondary"
                                    >
                                        Cancel
                                    </button>
                                )}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="relative">
                                    <img
                                        src={capturedImage}
                                        alt="Captured"
                                        className="w-full rounded-lg border-4 border-primary"
                                    />
                                </div>
                                <button
                                    onClick={resetDetection}
                                    className="w-full btn-secondary flex items-center justify-center space-x-2"
                                >
                                    <RefreshCw className="w-5 h-5" />
                                    <span>Retake Photo</span>
                                </button>
                            </div>
                        )}

                        <canvas ref={canvasRef} className="hidden" />
                    </div>

                    {/* Detection Controls & Results */}
                    <div className="space-y-6">
                        {/* Input Section */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-xl font-bold mb-4">Detection Settings</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Order UUID (optional)
                                    </label>
                                    <input
                                        type="text"
                                        value={orderUuid}
                                        onChange={(e) => setOrderUuid(e.target.value)}
                                        placeholder="e.g., order-123-abc"
                                        className="input-field"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Expected Products (comma-separated)
                                    </label>
                                    <textarea
                                        value={expectedProducts}
                                        onChange={(e) => setExpectedProducts(e.target.value)}
                                        placeholder="e.g., Milk Tetra Pack, Organic Oats, Brown Bread"
                                        rows={3}
                                        className="input-field resize-none"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Leave empty to just detect products without validation
                                    </p>
                                </div>

                                <button
                                    onClick={detectProducts}
                                    disabled={!capturedImage || isDetecting}
                                    className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                                >
                                    {isDetecting ? (
                                        <>
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                                            <span>Detecting...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Zap className="w-5 h-5" />
                                            <span>Detect Products</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Results Section */}
                        {detectionResult && (
                            <div className="bg-white rounded-xl shadow-sm p-6">
                                <h2 className="text-xl font-bold mb-4">Detection Results</h2>

                                {/* Status Badge */}
                                <div className={`rounded-lg p-4 mb-4 ${getStatusColor(detectionResult.match_status)}`}>
                                    <div className="flex items-center space-x-3">
                                        {getStatusIcon(detectionResult.match_status)}
                                        <div>
                                            <p className="font-bold text-lg capitalize">
                                                {detectionResult.match_status.replace('_', ' ')}
                                            </p>
                                            <p className="text-sm">
                                                Confidence: {(detectionResult.confidence_score * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Detected Products */}
                                <div className="space-y-3">
                                    <h3 className="font-semibold text-gray-700">Detected Products</h3>
                                    {detectionResult.detected_products.length > 0 ? (
                                        <div className="space-y-2">
                                            {detectionResult.detected_products.map((product, idx) => (
                                                <div key={idx} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                                                    <span className="font-medium">{product.name}</span>
                                                    <span className="text-sm text-gray-600">
                                                        {(product.confidence * 100).toFixed(1)}% confidence
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 text-sm">No products detected</p>
                                    )}
                                </div>

                                {/* Missing Products */}
                                {detectionResult.missing_products.length > 0 && (
                                    <div className="mt-4 space-y-2">
                                        <h3 className="font-semibold text-orange-600">Missing Products</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {detectionResult.missing_products.map((product, idx) => (
                                                <span key={idx} className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm">
                                                    {product}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Extra Products */}
                                {detectionResult.extra_products.length > 0 && (
                                    <div className="mt-4 space-y-2">
                                        <h3 className="font-semibold text-yellow-600">Extra Products</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {detectionResult.extra_products.map((product, idx) => (
                                                <span key={idx} className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-sm">
                                                    {product}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
