from sqlalchemy.orm import Session
from app.models.exit_qr import ExitQR
from app.models.order import Order
from app.models.order_item import OrderItem
from app.api.exit_qr.schemas import ExitQRGenerateRequest, ExitQRVerifyRequest
from app.core.security import create_qr_token, verify_qr_token
from app.utils.qr_generator import generate_qr_code
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from uuid import UUID
from app.config import settings

class ExitQRService:
    
    @staticmethod
    def generate_exit_qr(db: Session, request: ExitQRGenerateRequest):
        """Generate exit QR code after successful payment"""
        
        # Get order
        order = db.query(Order).filter(Order.order_uuid == request.order_uuid).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if order is paid or verified (verified means QR was already generated)
        if order.status not in ["paid", "verified"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order must be paid to generate exit QR. Current status: {order.status}"
            )
        
        # Check if exit QR already exists
        existing_qr = db.query(ExitQR).filter(
            ExitQR.order_uuid == request.order_uuid
        ).first()
        
        if existing_qr and not existing_qr.used:
            # Return existing QR if not used
            qr_image = generate_qr_code(existing_qr.token)
            return {
                "exit_qr_uuid": existing_qr.exit_qr_uuid,
                "order_uuid": order.order_uuid,
                "token": existing_qr.token,
                "qr_image": qr_image,
                "expires_at": existing_qr.expires_at.isoformat(),
                "order_number": order.order_number,
                "total_amount": order.total_amount,
                "message": "Exit QR code generated successfully"
            }
        
        # Generate new token
        expires_at = datetime.utcnow() + timedelta(minutes=settings.QR_EXPIRY_MINUTES)
        
        token_payload = {
            "order_uuid": str(order.order_uuid),
            "order_number": order.order_number,
            "amount": float(order.total_amount),
            "type": "exit_qr"
        }
        
        token = create_qr_token(token_payload)
        
        # Generate QR code image
        qr_image = generate_qr_code(token)
        
        # Create exit QR record
        exit_qr = ExitQR(
            order_uuid=order.order_uuid,
            token=token,
            expires_at=expires_at,
            used=False
        )
        
        db.add(exit_qr)
        
        # Update order status
        order.status = "verified"
        
        db.commit()
        db.refresh(exit_qr)
        
        return {
            "exit_qr_uuid": exit_qr.exit_qr_uuid,
            "order_uuid": order.order_uuid,
            "token": token,
            "qr_image": qr_image,
            "expires_at": expires_at.isoformat(),
            "order_number": order.order_number,
            "total_amount": order.total_amount,
            "message": "Exit QR code generated successfully"
        }
    
    @staticmethod
    def verify_exit_qr(db: Session, request: ExitQRVerifyRequest, staff_id: str = None):
        """Verify exit QR code at gate"""
        
        # Verify token
        payload = verify_qr_token(request.qr_token)
        
        if not payload:
            return {
                "valid": False,
                "message": "Invalid QR code",
                "status": "invalid"
            }
        
        order_uuid = payload.get("order_uuid")
        
        # Get exit QR record
        exit_qr = db.query(ExitQR).filter(ExitQR.token == request.qr_token).first()
        
        if not exit_qr:
            return {
                "valid": False,
                "message": "QR code not found",
                "status": "invalid"
            }
        
        # Check if already used
        if exit_qr.used:
            return {
                "valid": False,
                "message": "QR code already used",
                "status": "already_used"
            }
        
        # Check if expired
        if datetime.utcnow() > exit_qr.expires_at:
            return {
                "valid": False,
                "message": "QR code expired",
                "status": "expired"
            }
        
        # Get order details
        order = db.query(Order).filter(Order.order_uuid == order_uuid).first()
        
        if not order:
            return {
                "valid": False,
                "message": "Order not found",
                "status": "invalid"
            }
        
        # Get order items
        order_items = db.query(OrderItem).filter(
            OrderItem.order_uuid == order.order_uuid
        ).all()
        
        items_list = [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in order_items
        ]
        
        # Mark as used
        exit_qr.used = True
        exit_qr.used_at = datetime.utcnow()
        exit_qr.verified_by = staff_id
        
        db.commit()
        
        return {
            "valid": True,
            "order_uuid": order.order_uuid,
            "order_number": order.order_number,
            "user_name": order.user.name or order.user.phone_number,
            "total_amount": order.total_amount,
            "items_count": order.items_count,
            "items": items_list,
            "message": "Authorization successful. Customer can exit.",
            "status": "authorized"
        }
