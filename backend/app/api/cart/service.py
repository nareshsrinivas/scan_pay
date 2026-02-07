from sqlalchemy.orm import Session
from app.models.cart import Cart
from app.models.product import Product
from app.models.user import User
from app.api.cart.schemas import CartAddRequest
from fastapi import HTTPException, status
from uuid import UUID

TAX_RATE = 0.05  # 5% GST

class CartService:
    
    @staticmethod
    def add_to_cart(db: Session, user: User, request: CartAddRequest):
        """Add product to cart"""
        
        # Verify product exists and has stock
        product = db.query(Product).filter(
            Product.product_uuid == request.product_uuid,
            Product.is_active == 1
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        if product.stock < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.stock}"
            )
        
        # Check if item already in cart
        cart_item = db.query(Cart).filter(
            Cart.user_uuid == user.user_uuid,
            Cart.product_uuid == request.product_uuid
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += request.quantity
        else:
            # Create new cart item
            cart_item = Cart(
                user_uuid=user.user_uuid,
                product_uuid=request.product_uuid,
                quantity=request.quantity
            )
            db.add(cart_item)
        
        db.commit()
        db.refresh(cart_item)
        
        return CartService.get_cart(db, user)
    
    @staticmethod
    def get_cart(db: Session, user: User):
        """Get user's cart"""
        
        cart_items = db.query(Cart).filter(Cart.user_uuid == user.user_uuid).all()
        
        items = []
        subtotal = 0
        
        for cart_item in cart_items:
            product = cart_item.product
            item_subtotal = product.price * cart_item.quantity
            subtotal += item_subtotal
            
            items.append({
                "cart_uuid": cart_item.cart_uuid,
                "product_uuid": product.product_uuid,
                "product_name": product.name,
                "product_sku": product.sku,
                "product_price": product.price,
                "product_image": product.image_url,
                "quantity": cart_item.quantity,
                "subtotal": item_subtotal
            })
        
        tax_amount = subtotal * TAX_RATE
        total_amount = subtotal + tax_amount
        
        return {
            "items": items,
            "total_items": len(items),
            "subtotal": round(subtotal, 2),
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(total_amount, 2)
        }
    
    @staticmethod
    def update_cart_item(db: Session, user: User, cart_uuid: UUID, quantity: int):
        """Update cart item quantity"""
        
        cart_item = db.query(Cart).filter(
            Cart.cart_uuid == cart_uuid,
            Cart.user_uuid == user.user_uuid
        ).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        if quantity == 0:
            # Remove item
            db.delete(cart_item)
        else:
            # Check stock
            if cart_item.product.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {cart_item.product.stock}"
                )
            cart_item.quantity = quantity
        
        db.commit()
        
        return CartService.get_cart(db, user)
    
    @staticmethod
    def remove_from_cart(db: Session, user: User, cart_uuid: UUID):
        """Remove item from cart"""
        
        cart_item = db.query(Cart).filter(
            Cart.cart_uuid == cart_uuid,
            Cart.user_uuid == user.user_uuid
        ).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        db.delete(cart_item)
        db.commit()
        
        return {"message": "Item removed from cart"}
    
    @staticmethod
    def clear_cart(db: Session, user: User):
        """Clear entire cart"""
        
        db.query(Cart).filter(Cart.user_uuid == user.user_uuid).delete()
        db.commit()
        
        return {"message": "Cart cleared successfully"}
