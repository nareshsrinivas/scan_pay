from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart import Cart
from app.models.user import User
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from uuid import UUID
import random
import string

TAX_RATE = 0.05

class OrderService:
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"ORD-{timestamp}-{random_part}"
    
    @staticmethod
    def create_order(db: Session, user: User):
        """Create order from cart"""
        
        # Get cart items
        cart_items = db.query(Cart).filter(Cart.user_uuid == user.user_uuid).all()
        
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Calculate totals
        subtotal = 0
        items_count = 0
        
        for cart_item in cart_items:
            subtotal += cart_item.product.price * cart_item.quantity
            items_count += cart_item.quantity
            
            # Check stock
            if cart_item.product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {cart_item.product.name}"
                )
        
        tax_amount = subtotal * TAX_RATE
        total_amount = subtotal + tax_amount
        
        # Create order
        order = Order(
            user_uuid=user.user_uuid,
            order_number=OrderService.generate_order_number(),
            subtotal=round(subtotal, 2),
            tax_amount=round(tax_amount, 2),
            total_amount=round(total_amount, 2),
            items_count=items_count,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        db.add(order)
        db.flush()  # Get order UUID
        
        # Create order items
        for cart_item in cart_items:
            product = cart_item.product
            order_item = OrderItem(
                order_uuid=order.order_uuid,
                product_uuid=product.product_uuid,
                product_name=product.name,
                product_sku=product.sku,
                price=product.price,
                quantity=cart_item.quantity,
                subtotal=product.price * cart_item.quantity
            )
            db.add(order_item)
        
        # Clear cart
        db.query(Cart).filter(Cart.user_uuid == user.user_uuid).delete()
        
        db.commit()
        db.refresh(order)
        
        return {
            "order_uuid": order.order_uuid,
            "order_number": order.order_number,
            "total_amount": order.total_amount,
            "status": order.status,
            "message": "Order created successfully. Please proceed to payment."
        }
    
    @staticmethod
    def get_order(db: Session, order_uuid: UUID, user: User = None):
        """Get order by UUID"""
        
        query = db.query(Order).filter(Order.order_uuid == order_uuid)
        
        if user:
            query = query.filter(Order.user_uuid == user.user_uuid)
        
        order = query.first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get order items
        order_items = db.query(OrderItem).filter(
            OrderItem.order_uuid == order_uuid
        ).all()
        
        return {
            "order_uuid": order.order_uuid,
            "order_number": order.order_number,
            "user_uuid": order.user_uuid,
            "subtotal": order.subtotal,
            "tax_amount": order.tax_amount,
            "total_amount": order.total_amount,
            "status": order.status,
            "items_count": order.items_count,
            "created_at": order.created_at.isoformat(),
            "expires_at": order.expires_at.isoformat() if order.expires_at else None,
            "items": [
                {
                    "order_item_uuid": item.order_item_uuid,
                    "product_uuid": item.product_uuid,
                    "product_name": item.product_name,
                    "product_sku": item.product_sku,
                    "price": item.price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal
                }
                for item in order_items
            ]
        }
    
    @staticmethod
    def get_user_orders(db: Session, user: User):
        """Get all orders for user"""
        
        orders = db.query(Order).filter(
            Order.user_uuid == user.user_uuid
        ).order_by(Order.created_at.desc()).all()
        
        return [
            OrderService.get_order(db, order.order_uuid, user)
            for order in orders
        ]
