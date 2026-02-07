"""
Updated Payment Routes
Supports both Demo and Razorpay modes
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
import json
import httpx

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.api.payments.schemas import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentWebhookRequest,
    PaymentStatusResponse,
    PaymentVerifyRequest
)
from app.config import settings

# Import payment services
from app.services.demo_payment import demo_payment_service
from app.services.razorpay_service import razorpay_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    request: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate payment for an order
    Supports both demo and Razorpay modes based on PAYMENT_MODE setting
    """
    
    # Get order
    order = db.query(Order).filter(Order.order_uuid == request.order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order.user_uuid != current_user.user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if already paid
    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    # Get payment mode from settings
    payment_mode = settings.PAYMENT_MODE  # "demo" or "razorpay"
    
    if payment_mode == "demo":
        # Demo payment - simulate payment flow
        demo_response = await demo_payment_service.create_payment(
            order_uuid=str(order.order_uuid),
            amount=float(order.total_amount),
            payment_method=request.payment_method,
            simulate_failure=request.simulate_failure
        )
        
        # Create payment record
        payment = Payment(
            order_uuid=order.order_uuid,
            amount=order.total_amount,
            payment_method=request.payment_method,
            payment_provider="demo",
            transaction_id=demo_response.transaction_id,
            status="pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return PaymentInitiateResponse(
            payment_uuid=str(payment.payment_uuid),
            order_uuid=str(order.order_uuid),
            amount=float(order.total_amount),
            currency="INR",
            payment_method=request.payment_method,
            payment_url=demo_response.payment_url,
            qr_code=demo_response.qr_code,
            provider="demo",
            provider_payment_id=demo_response.transaction_id,
            expires_at=None,
            status="pending"
        )
    
    elif payment_mode == "razorpay":
        # Razorpay payment - production flow
        try:
            razorpay_order = razorpay_service.create_order(
                order_uuid=str(order.order_uuid),
                amount=float(order.total_amount),
                notes={
                    "order_uuid": str(order.order_uuid),
                    "user_uuid": str(current_user.user_uuid)
                }
            )
            
            # Create payment record
            payment = Payment(
                order_uuid=order.order_uuid,
                amount=order.total_amount,
                payment_method=request.payment_method,
                payment_provider="razorpay",
                transaction_id=razorpay_order.razorpay_order_id,
                status="pending"
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            return PaymentInitiateResponse(
                payment_uuid=str(payment.payment_uuid),
                order_uuid=str(order.order_uuid),
                amount=float(order.total_amount),
                currency=razorpay_order.currency,
                payment_method=request.payment_method,
                payment_url=None,  # Razorpay uses SDK, not direct URL
                qr_code=None,
                provider="razorpay",
                provider_payment_id=razorpay_order.razorpay_order_id,
                razorpay_key_id=razorpay_order.key_id,
                expires_at=None,
                status="pending"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment initiation failed: {str(e)}"
            )
    
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid payment mode: {payment_mode}"
        )


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle payment webhook from gateway
    Supports both demo and Razorpay webhooks
    """
    
    # Get raw body
    body = await request.body()
    body_str = body.decode()
    
    # Parse JSON
    try:
        data = json.loads(body_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Determine webhook type
    if "event" in data and data["event"].startswith("payment"):
        # Razorpay webhook
        if not x_razorpay_signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify signature
        is_valid = razorpay_service.verify_webhook_signature(
            webhook_body=body_str,
            webhook_signature=x_razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Process Razorpay webhook
        return await process_razorpay_webhook(data, db)
    
    else:
        # Demo webhook
        return await process_demo_webhook(data, db)


async def process_demo_webhook(data: dict, db: Session):
    """Process demo payment webhook"""
    
    order_uuid = data.get("order_uuid")
    payment_uuid = data.get("payment_uuid")
    status = data.get("status")
    
    if not order_uuid:
        raise HTTPException(status_code=400, detail="Missing order_uuid")
    
    # Find order
    order = db.query(Order).filter(Order.order_uuid == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status
    if status == "success":
        order.status = "paid"
        
        # Update payment record
        payment = db.query(Payment).filter(Payment.order_uuid == order_uuid).first()
        if payment:
            payment.status = "success"
            payment.upi_txn_id = data.get("provider_reference")
        
        # Trigger n8n webhook if enabled
        if settings.N8N_ENABLED and settings.N8N_WEBHOOK_URL:
            await trigger_n8n_webhook(data)
    
    else:
        order.status = "payment_failed"
        
        payment = db.query(Payment).filter(Payment.order_uuid == order_uuid).first()
        if payment:
            payment.status = "failed"
    
    db.commit()
    
    return {
        "success": True,
        "message": "Webhook processed"
    }


async def process_razorpay_webhook(data: dict, db: Session):
    """Process Razorpay payment webhook"""
    
    event = data.get("event")
    payload = data.get("payload", {}).get("payment", {}).get("entity", {})
    
    if event == "payment.captured":
        # Payment successful
        notes = payload.get("notes", {})
        order_uuid = notes.get("order_uuid")
        payment_id = payload.get("id")
        
        if not order_uuid:
            return {"success": False, "message": "Order UUID not found in notes"}
        
        # Find order
        order = db.query(Order).filter(Order.order_uuid == order_uuid).first()
        if not order:
            return {"success": False, "message": "Order not found"}
        
        # Update order
        order.status = "paid"
        
        # Update payment
        payment = db.query(Payment).filter(
            Payment.order_uuid == order.order_uuid
        ).first()
        
        if payment:
            payment.status = "success"
            payment.upi_txn_id = payment_id
        
        db.commit()
        
        # Trigger n8n webhook if enabled
        if settings.N8N_ENABLED and settings.N8N_WEBHOOK_URL:
            await trigger_n8n_webhook({
                "order_uuid": str(order_uuid),
                "payment_id": payment_id,
                "status": "success",
                "amount": payload.get("amount", 0) / 100
            })
        
        return {"success": True, "message": "Payment captured"}
    
    elif event == "payment.failed":
        # Payment failed
        notes = data.get("payload", {}).get("payment", {}).get("entity", {}).get("notes", {})
        order_uuid = notes.get("order_uuid")
        
        if order_uuid:
            order = db.query(Order).filter(Order.order_uuid == order_uuid).first()
            if order:
                order.status = "payment_failed"
                
                payment = db.query(Payment).filter(
                    Payment.order_uuid == order.order_uuid
                ).first()
                if payment:
                    payment.status = "failed"
                
                db.commit()
        
        return {"success": True, "message": "Payment failed event processed"}
    
    return {"success": True, "message": "Event processed"}


async def trigger_n8n_webhook(data: dict):
    """Trigger n8n workflow via webhook"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                settings.N8N_WEBHOOK_URL,
                json=data,
                timeout=10.0
            )
    except Exception as e:
        print(f"Failed to trigger n8n webhook: {e}")


@router.post("/verify-razorpay")
async def verify_razorpay_payment(
    request: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment on frontend
    Called after customer completes payment via Razorpay SDK
    """
    
    # Verify signature
    is_valid = razorpay_service.verify_payment_signature(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # Find payment by provider_payment_id (razorpay_order_id)
    payment = db.query(Payment).filter(
        Payment.transaction_id == request.razorpay_order_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Update payment status
    payment.status = "success"
    payment.upi_txn_id = request.razorpay_payment_id
    
    # Update order status
    order = db.query(Order).filter(Order.order_uuid == payment.order_uuid).first()
    if order:
        order.status = "paid"
    
    db.commit()
    
    # Trigger n8n webhook if enabled
    if settings.N8N_ENABLED and settings.N8N_WEBHOOK_URL:
        await trigger_n8n_webhook({
            "order_uuid": str(payment.order_uuid),
            "payment_id": request.razorpay_payment_id,
            "status": "success"
        })
    
    return {
        "success": True,
        "message": "Payment verified",
        "order_uuid": str(payment.order_uuid)
    }


@router.get("/{payment_uuid}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status"""
    
    payment = db.query(Payment).filter(Payment.payment_uuid == payment_uuid).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify ownership
    order = db.query(Order).filter(Order.order_uuid == payment.order_uuid).first()
    if order and order.user_uuid != current_user.user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return PaymentStatusResponse(
        payment_uuid=str(payment.payment_uuid),
        order_uuid=str(payment.order_uuid),
        amount=float(payment.amount),
        status=payment.status,
        payment_method=payment.payment_method,
        provider=payment.payment_provider,
        provider_payment_id=payment.transaction_id,
        provider_reference=payment.upi_txn_id,
        created_at=payment.created_at,
        updated_at=None
    )


@router.post("/demo/complete/{order_uuid}")
async def demo_complete_payment(
    order_uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete a demo payment manually
    This simulates what would happen after UPI payment is confirmed
    """
    
    if settings.PAYMENT_MODE != "demo":
        raise HTTPException(status_code=400, detail="Demo mode is not enabled")
    
    # Find order
    order = db.query(Order).filter(Order.order_uuid == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_uuid != current_user.user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    # Update order
    order.status = "paid"
    
    # Update payment
    payment = db.query(Payment).filter(Payment.order_uuid == order_uuid).first()
    if payment:
        payment.status = "success"
    
    db.commit()
    
    # Trigger n8n webhook if enabled
    if settings.N8N_ENABLED and settings.N8N_WEBHOOK_URL:
        await trigger_n8n_webhook({
            "order_uuid": str(order_uuid),
            "status": "success"
        })
    
    return {
        "success": True,
        "message": "Demo payment completed",
        "order_uuid": str(order_uuid)
    }
