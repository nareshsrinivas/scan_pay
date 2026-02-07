"""
Razorpay Payment Integration Service
Production-ready payment processing
"""

import razorpay
import hmac
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from app.config import get_settings

settings = get_settings()


class RazorpayPaymentRequest(BaseModel):
    order_uuid: str
    amount: float
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[Dict[str, str]] = None


class RazorpayPaymentResponse(BaseModel):
    razorpay_order_id: str
    order_uuid: str
    amount: int  # Amount in paise
    currency: str
    status: str
    created_at: int
    key_id: str  # For frontend


class RazorpayService:
    """
    Handles all Razorpay payment operations
    """
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    
    def create_order(
        self,
        order_uuid: str,
        amount: float,
        currency: str = "INR",
        notes: Optional[Dict[str, str]] = None
    ) -> RazorpayPaymentResponse:
        """
        Create a Razorpay order
        
        Args:
            order_uuid: Internal order UUID
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            notes: Additional notes
            
        Returns:
            Razorpay order details
        """
        
        # Convert rupees to paise (Razorpay uses smallest currency unit)
        amount_in_paise = int(amount * 100)
        
        # Prepare order data
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": order_uuid,
            "notes": notes or {"order_uuid": order_uuid}
        }
        
        try:
            # Create order via Razorpay API
            razorpay_order = self.client.order.create(data=order_data)
            
            return RazorpayPaymentResponse(
                razorpay_order_id=razorpay_order["id"],
                order_uuid=order_uuid,
                amount=razorpay_order["amount"],
                currency=razorpay_order["currency"],
                status=razorpay_order["status"],
                created_at=razorpay_order["created_at"],
                key_id=settings.RAZORPAY_KEY_ID
            )
            
        except razorpay.errors.BadRequestError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Razorpay order creation failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment gateway error: {str(e)}"
            )
    
    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature
        This ensures the payment callback is authentic
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Signature from Razorpay
            
        Returns:
            True if signature is valid
        """
        
        try:
            # Verify signature using Razorpay utility
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
            
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def verify_webhook_signature(
        self,
        webhook_body: str,
        webhook_signature: str
    ) -> bool:
        """
        Verify webhook signature from Razorpay
        
        Args:
            webhook_body: Raw webhook body (string)
            webhook_signature: X-Razorpay-Signature header
            
        Returns:
            True if signature is valid
        """
        
        try:
            # Generate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                webhook_body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, webhook_signature)
            
        except Exception as e:
            print(f"Webhook signature verification error: {e}")
            return False
    
    def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Fetch payment details from Razorpay
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment details
        """
        
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch payment: {str(e)}"
            )
    
    def capture_payment(
        self,
        payment_id: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Capture an authorized payment
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount in paise
            
        Returns:
            Captured payment details
        """
        
        try:
            return self.client.payment.capture(payment_id, amount)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment capture failed: {str(e)}"
            )
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[int] = None,
        notes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial)
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund in paise (None = full refund)
            notes: Refund notes
            
        Returns:
            Refund details
        """
        
        refund_data = {}
        if amount:
            refund_data["amount"] = amount
        if notes:
            refund_data["notes"] = notes
        
        try:
            return self.client.payment.refund(payment_id, refund_data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Refund failed: {str(e)}"
            )
    
    def fetch_order(self, order_id: str) -> Dict[str, Any]:
        """
        Fetch order details from Razorpay
        
        Args:
            order_id: Razorpay order ID
            
        Returns:
            Order details
        """
        
        try:
            return self.client.order.fetch(order_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch order: {str(e)}"
            )
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """
        Get available payment methods
        
        Returns:
            Available payment methods
        """
        
        try:
            return self.client.method.all()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch payment methods: {str(e)}"
            )


# Singleton instance
razorpay_service = RazorpayService()


# Helper functions for common operations

def create_razorpay_order(order_uuid: str, amount: float) -> Dict[str, Any]:
    """Quick helper to create a Razorpay order"""
    return razorpay_service.create_order(
        order_uuid=order_uuid,
        amount=amount,
        notes={"order_uuid": order_uuid}
    )


def verify_razorpay_payment(
    order_id: str,
    payment_id: str,
    signature: str
) -> bool:
    """Quick helper to verify payment signature"""
    return razorpay_service.verify_payment_signature(
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=signature
    )
