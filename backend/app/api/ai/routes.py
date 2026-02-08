"""
AI Service Routes - Face Detection using YOLOv8
Integrated into main backend from ai_service
Uses pretrained YOLOv8 face detection model
"""

from fastapi import APIRouter, HTTPException
import base64
import io
import os
from PIL import Image
import numpy as np
from typing import List, Optional

from .schemas import (
    DetectionRequest,
    DetectedProduct,
    DetectionResponse,
    AIHealthResponse
)

# Get the model path relative to this file
MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "ai_service", "app", "models", "models_data"
)
FACE_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n-face.pt")

# YOLOv8 imports
try:
    from ultralytics import YOLO
    import cv2
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLOv8 not installed. AI service will run in demo mode.")

router = APIRouter(prefix="/ai", tags=["AI Detection"])


class FaceDetector:
    """
    Face detection using YOLOv8 face model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or FACE_MODEL_PATH
        self.model = None
        self.demo_mode = not YOLO_AVAILABLE
        
        print(f"🔍 Looking for model at: {self.model_path}")
        
        if not self.demo_mode:
            if os.path.exists(self.model_path):
                try:
                    self.model = YOLO(self.model_path)
                    print(f"✅ YOLOv8 Face model loaded: {self.model_path}")
                except Exception as e:
                    print(f"⚠️  Failed to load model: {e}")
                    print("    Running in demo mode")
                    self.demo_mode = True
            else:
                print(f"⚠️  Model file not found: {self.model_path}")
                print("    Running in demo mode")
                self.demo_mode = True
        
        # For face detection, we just have one class
        self.detection_classes = {
            0: "Face"
        }
    
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[DetectedProduct]:
        """
        Detect faces in image
        """
        
        if self.demo_mode:
            return self._demo_detect(image)
        
        try:
            # Convert RGB to BGR for OpenCV/YOLO if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            results = self.model(image_bgr, conf=confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    detection_name = self.detection_classes.get(class_id, f"Face_{class_id}")
                    
                    detections.append(DetectedProduct(
                        name=detection_name,
                        confidence=confidence,
                        bbox=[int(x1), int(y1), int(x2), int(y2)]
                    ))
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _demo_detect(self, image: np.ndarray) -> List[DetectedProduct]:
        """Demo mode - return simulated face detections"""
        # Simulate detecting a face in the center of the image
        h, w = image.shape[:2] if len(image.shape) >= 2 else (480, 640)
        center_x, center_y = w // 2, h // 2
        face_size = min(w, h) // 4
        
        return [
            DetectedProduct(
                name="Face",
                confidence=0.95,
                bbox=[
                    center_x - face_size, 
                    center_y - face_size, 
                    center_x + face_size, 
                    center_y + face_size
                ]
            )
        ]
    
    def validate_order(
        self,
        detected_products: List[DetectedProduct],
        expected_products: List[str]
    ) -> tuple:
        """
        Validate detected items against expected list
        For face detection: just check if faces were found
        """
        
        detected_names = [p.name for p in detected_products]
        missing = [p for p in expected_products if p not in detected_names]
        extra = [p for p in detected_names if p not in expected_products]
        
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
        
        if detected_products:
            avg_confidence = sum(p.confidence for p in detected_products) / len(detected_products)
        else:
            avg_confidence = 0.0
        
        return match_status, missing, extra, avg_confidence


# Initialize detector with the face model
detector = FaceDetector()


@router.get("/health", response_model=AIHealthResponse)
async def ai_health():
    """Health check endpoint for AI service"""
    return AIHealthResponse(
        status="healthy",
        demo_mode=detector.demo_mode,
        model_loaded=detector.model is not None
    )


@router.post("/detect-products", response_model=DetectionResponse)
async def detect_products(request: DetectionRequest):
    """
    Detect faces/objects in image and validate against expected list
    """
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array (RGB)
        image_np = np.array(image)
        
        # Detect faces
        detected_items = detector.detect(image_np)
        
        # Validate against expected
        match_status, missing, extra, confidence = detector.validate_order(
            detected_products=detected_items,
            expected_products=request.expected_products
        )
        
        return DetectionResponse(
            success=True,
            detected_products=detected_items,
            match_status=match_status,
            expected_products=request.expected_products,
            missing_products=missing,
            extra_products=extra,
            confidence_score=confidence
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )
