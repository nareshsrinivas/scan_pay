from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.order import Order
from app.models.order_item import OrderItem
from app.api.payments.schemas import PaymentInitiateRequest, PaymentWebhookRequest
from fastapi import HTTPException, status
from datetime import datetime
from uuid import UUID
import httpx
from app.config import settings

class PaymentService:
    
    @staticmethod
    def initiate_payment(db: Session, request: PaymentInitiateRequest):
        """Initiate payment for an order"""
        
        # Get order
        order = db.query(Order).filter(Order.order_uuid == request.order_uuid).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is already {order.status}"
            )
        
        # Check if payment already exists
        existing_payment = db.query(Payment).filter(
            Payment.order_uuid == request.order_uuid
        ).first()
        
        if existing_payment and existing_payment.status == "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already completed for this order"
            )
        
        # Create or update payment record
        if existing_payment:
            payment = existing_payment
        else:
            payment = Payment(
                order_uuid=request.order_uuid,
                payment_provider=request.payment_provider,
                amount=order.total_amount,
                status="pending"
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
        
        # In production, integrate with actual payment gateway
        # For now, return mock payment URL
        payment_url = f"https://payment-gateway.com/pay/{payment.payment_uuid}"
        
        return {
            "payment_uuid": payment.payment_uuid,
            "order_uuid": order.order_uuid,
            "amount": order.total_amount,
            "payment_provider": request.payment_provider,
            "payment_url": payment_url,
            "payment_id": str(payment.payment_uuid),
            "message": "Payment initiated. Redirect user to payment URL."
        }
    
    @staticmethod
    async def handle_payment_webhook(db: Session, request: PaymentWebhookRequest):
        """Handle payment webhook from payment gateway"""
        
        # Get order
        order = db.query(Order).filter(Order.order_uuid == request.order_uuid).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get payment
        payment = db.query(Payment).filter(
            Payment.order_uuid == request.order_uuid
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Verify signature (implement actual signature verification in production)
        # For now, trust the webhook
        
        # Update payment status
        payment.status = request.status
        payment.transaction_id = request.transaction_id
        payment.upi_txn_id = request.transaction_id
        payment.payment_method = request.payment_method
        payment.gateway_response = str(request.dict())
        
        if request.status == "success":
            payment.paid_at = datetime.utcnow()
            order.status = "paid"
            
            # Reduce stock for products
            order_items = db.query(OrderItem).filter(
                OrderItem.order_uuid == order.order_uuid
            ).all()
            
            for item in order_items:
                product = item.product
                if product:
                    product.stock -= item.quantity
            
            # Trigger n8n workflow
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        settings.N8N_WEBHOOK_URL,
                        json={
                            "event": "payment_success",
                            "order_uuid": str(order.order_uuid),
                            "order_number": order.order_number,
                            "amount": float(order.total_amount),
                            "user_uuid": str(order.user_uuid),
                            "transaction_id": request.transaction_id
                        },
                        timeout=5.0
                    )
            except Exception as e:
                print(f"n8n webhook failed: {e}")
                # Don't fail the payment if webhook fails
        
        elif request.status == "failed":
            order.status = "failed"
        
        db.commit()
        db.refresh(payment)
        db.refresh(order)
        
        return {
            "success": True,
            "message": "Payment webhook processed",
            "order_status": order.status,
            "payment_status": payment.status
        }
    
    @staticmethod
    def get_payment_status(db: Session, payment_uuid: UUID):
        """Get payment status"""
        
        payment = db.query(Payment).filter(
            Payment.payment_uuid == payment_uuid
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return {
            "payment_uuid": payment.payment_uuid,
            "order_uuid": payment.order_uuid,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "amount": payment.amount,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
        }
