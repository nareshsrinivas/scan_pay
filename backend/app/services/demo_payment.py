"""
Demo Payment Service - For Testing/Showcase
Simulates payment without real gateway
"""

import uuid
import random
import asyncio
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DemoPaymentRequest(BaseModel):
    order_uuid: str
    amount: float
    payment_method: str = "upi"
    simulate_failure: bool = False


class DemoPaymentResponse(BaseModel):
    payment_uuid: str
    transaction_id: str
    order_uuid: str
    amount: float
    status: str
    payment_method: str
    payment_url: Optional[str]
    qr_code: Optional[str]
    timestamp: datetime


class DemoPaymentService:
    """
    Simulates payment gateway behavior for testing
    """
    
    def __init__(self, delay_seconds: int = 3, failure_rate: int = 0):
        self.delay_seconds = delay_seconds
        self.failure_rate = failure_rate  # 0-100
    
    async def create_payment(
        self, 
        order_uuid: str, 
        amount: float,
        payment_method: str = "upi",
        simulate_failure: bool = False
    ) -> DemoPaymentResponse:
        """
        Create a demo payment
        
        Args:
            order_uuid: Order UUID
            amount: Amount to pay
            payment_method: Payment method (upi, card, etc.)
            simulate_failure: Force failure for testing
            
        Returns:
            Demo payment response
        """
        
        payment_uuid = str(uuid.uuid4())
        transaction_id = f"DEMO_TXN_{random.randint(1000000000, 9999999999)}"
        
        # Simulate payment processing delay
        await asyncio.sleep(self.delay_seconds)
        
        # Determine if payment should fail
        should_fail = simulate_failure or (random.randint(1, 100) <= self.failure_rate)
        
        if should_fail:
            return DemoPaymentResponse(
                payment_uuid=payment_uuid,
                transaction_id=transaction_id,
                order_uuid=order_uuid,
                amount=amount,
                status="failed",
                payment_method=payment_method,
                payment_url=None,
                qr_code=None,
                timestamp=datetime.utcnow()
            )
        
        # Generate demo UPI QR code data
        upi_qr = self._generate_upi_qr(amount, transaction_id)
        payment_url = f"https://demo-payment.smartcheckout.com/pay/{transaction_id}"
        
        return DemoPaymentResponse(
            payment_uuid=payment_uuid,
            transaction_id=transaction_id,
            order_uuid=order_uuid,
            amount=amount,
            status="success",
            payment_method=payment_method,
            payment_url=payment_url,
            qr_code=upi_qr,
            timestamp=datetime.utcnow()
        )
    
    def _generate_upi_qr(self, amount: float, transaction_id: str) -> str:
        """Generate demo UPI QR code string"""
        return f"upi://pay?pa=merchant@upi&pn=SmartCheckout&am={amount}&cu=INR&tn={transaction_id}"
    
    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verify if payment was successful
        In demo mode, always return True for DEMO_TXN_* transactions
        """
        return transaction_id.startswith("DEMO_TXN_")
    
    async def process_webhook(self, data: dict) -> dict:
        """
        Process demo webhook
        Simulates what a real payment gateway would send
        """
        
        # Simulate webhook delay
        await asyncio.sleep(1)
        
        return {
            "event": "payment.success",
            "payload": {
                "payment": {
                    "id": data.get("payment_uuid"),
                    "order_id": data.get("order_uuid"),
                    "amount": data.get("amount"),
                    "status": "captured",
                    "method": data.get("payment_method", "upi")
                }
            },
            "created_at": datetime.utcnow().isoformat()
        }


# Singleton instance
demo_payment_service = DemoPaymentService(
    delay_seconds=3,  # Configurable via ENV
    failure_rate=0     # 0% failure rate by default
)
