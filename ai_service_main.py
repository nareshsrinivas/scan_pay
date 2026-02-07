"""
AI Service - Product Detection using YOLOv8
Detects products in images and validates against orders
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
from PIL import Image
import numpy as np
import cv2

# YOLOv8 imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLOv8 not installed. AI service will run in demo mode.")

app = FastAPI(
    title="Smart Checkout AI Service",
    description="Product detection and validation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectionRequest(BaseModel):
    image: str  # Base64 encoded image
    order_uuid: str
    expected_products: List[str]  # List of product names


class DetectedProduct(BaseModel):
    name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]


class DetectionResponse(BaseModel):
    success: bool
    detected_products: List[DetectedProduct]
    match_status: str  # "matched", "partial", "mismatch"
    expected_products: List[str]
    missing_products: List[str]
    extra_products: List[str]
    confidence_score: float


class ProductDetector:
    """
    Product detection using YOLOv8
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "yolov8n.pt"  # Default to nano model
        self.model = None
        self.demo_mode = not YOLO_AVAILABLE
        
        if not self.demo_mode:
            try:
                self.model = YOLO(self.model_path)
                print(f"✅ YOLOv8 model loaded: {self.model_path}")
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")
                print("    Running in demo mode")
                self.demo_mode = True
        
        # Product class mapping (customize based on your products)
        self.product_classes = {
            0: "Milk Tetra Pack",
            1: "Organic Oats",
            2: "Brown Bread",
            3: "Fresh Eggs",
            4: "Orange Juice",
            5: "Yogurt",
            6: "Cheese",
            7: "Butter"
        }
    
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[DetectedProduct]:
        """
        Detect products in image
        
        Args:
            image: OpenCV image (numpy array)
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of detected products
        """
        
        if self.demo_mode:
            # Demo mode - return mock detections
            return self._demo_detect(image)
        
        try:
            # Run YOLOv8 inference
            results = self.model(image, conf=confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Get confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Get product name
                    product_name = self.product_classes.get(class_id, f"Product_{class_id}")
                    
                    detections.append(DetectedProduct(
                        name=product_name,
                        confidence=confidence,
                        bbox=[int(x1), int(y1), int(x2), int(y2)]
                    ))
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def _demo_detect(self, image: np.ndarray) -> List[DetectedProduct]:
        """Demo mode - return simulated detections"""
        
        height, width = image.shape[:2]
        
        # Return mock detections
        return [
            DetectedProduct(
                name="Milk Tetra Pack",
                confidence=0.92,
                bbox=[100, 150, 200, 350]
            ),
            DetectedProduct(
                name="Organic Oats",
                confidence=0.88,
                bbox=[250, 120, 350, 340]
            )
        ]
    
    def validate_order(
        self,
        detected_products: List[DetectedProduct],
        expected_products: List[str]
    ) -> tuple[str, List[str], List[str], float]:
        """
        Validate detected products against order
        
        Returns:
            match_status, missing_products, extra_products, confidence_score
        """
        
        # Extract detected product names
        detected_names = [p.name for p in detected_products]
        
        # Find missing products
        missing = [p for p in expected_products if p not in detected_names]
        
        # Find extra products
        extra = [p for p in detected_names if p not in expected_products]
        
        # Calculate match status
        if not missing and not extra:
            match_status = "matched"
        elif missing or extra:
            if len(missing) == 0:
                match_status = "extra_items"
            elif len(extra) == 0:
                match_status = "missing_items"
            else:
                match_status = "mismatch"
        else:
            match_status = "matched"
        
        # Calculate average confidence
        if detected_products:
            avg_confidence = sum(p.confidence for p in detected_products) / len(detected_products)
        else:
            avg_confidence = 0.0
        
        return match_status, missing, extra, avg_confidence


# Initialize detector
detector = ProductDetector()


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Smart Checkout AI Service",
        "version": "1.0.0",
        "status": "healthy",
        "demo_mode": detector.demo_mode
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demo_mode": detector.demo_mode,
        "model_loaded": detector.model is not None
    }


@app.post("/detect-products", response_model=DetectionResponse)
async def detect_products(request: DetectionRequest):
    """
    Detect products in image and validate against order
    
    Args:
        request: Detection request with base64 image and expected products
        
    Returns:
        Detection results with validation
    """
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect products
        detected_products = detector.detect(image_cv)
        
        # Validate against order
        match_status, missing, extra, confidence = detector.validate_order(
            detected_products=detected_products,
            expected_products=request.expected_products
        )
        
        return DetectionResponse(
            success=True,
            detected_products=detected_products,
            match_status=match_status,
            expected_products=request.expected_products,
            missing_products=missing,
            extra_products=extra,
            confidence_score=confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


@app.post("/detect-image")
async def detect_from_upload(
    file: UploadFile = File(...),
    expected_products: Optional[str] = None
):
    """
    Detect products from uploaded image file
    
    Args:
        file: Image file
        expected_products: Comma-separated list of expected products
        
    Returns:
        Detection results
    """
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect products
        detected_products = detector.detect(image_cv)
        
        # Parse expected products
        expected = []
        if expected_products:
            expected = [p.strip() for p in expected_products.split(",")]
        
        # Validate if expected products provided
        if expected:
            match_status, missing, extra, confidence = detector.validate_order(
                detected_products=detected_products,
                expected_products=expected
            )
        else:
            match_status = "detection_only"
            missing = []
            extra = []
            confidence = sum(p.confidence for p in detected_products) / len(detected_products) if detected_products else 0.0
        
        return DetectionResponse(
            success=True,
            detected_products=detected_products,
            match_status=match_status,
            expected_products=expected,
            missing_products=missing,
            extra_products=extra,
            confidence_score=confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


@app.post("/train")
async def train_model(
    images_path: str,
    epochs: int = 100,
    batch_size: int = 16
):
    """
    Train custom YOLOv8 model on store products
    
    Args:
        images_path: Path to training images
        epochs: Number of training epochs
        batch_size: Batch size
        
    Returns:
        Training results
    """
    
    if detector.demo_mode:
        return {
            "success": False,
            "message": "Training not available in demo mode"
        }
    
    try:
        # Train model
        results = detector.model.train(
            data=images_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=640,
            device='cuda' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'cpu'
        )
        
        return {
            "success": True,
            "message": "Training completed",
            "results": str(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
