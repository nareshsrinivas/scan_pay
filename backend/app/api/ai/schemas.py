"""
Pydantic schemas for AI service
"""
from pydantic import BaseModel
from typing import List


class DetectionRequest(BaseModel):
    """Request schema for product detection"""
    image: str  # Base64 encoded image
    order_uuid: str
    expected_products: List[str]  # List of product names


class DetectedProduct(BaseModel):
    """Schema for a detected product"""
    name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]


class DetectionResponse(BaseModel):
    """Response schema for product detection"""
    success: bool
    detected_products: List[DetectedProduct]
    match_status: str  # "matched", "partial", "mismatch", "extra_items", "missing_items"
    expected_products: List[str]
    missing_products: List[str]
    extra_products: List[str]
    confidence_score: float


class AIHealthResponse(BaseModel):
    """Health check response for AI service"""
    status: str
    demo_mode: bool
    model_loaded: bool
