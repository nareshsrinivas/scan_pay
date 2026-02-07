from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.cart.schemas import CartAddRequest, CartResponse, CartUpdateRequest
from app.api.cart.service import CartService
from app.core.dependencies import get_current_user
from app.models.user import User
from uuid import UUID

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add", response_model=CartResponse)
async def add_to_cart(
    request: CartAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add product to cart
    """
    return CartService.add_to_cart(db, current_user, request)

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's cart
    """
    return CartService.get_cart(db, current_user)

@router.put("/{cart_uuid}", response_model=CartResponse)
async def update_cart_item(
    cart_uuid: UUID,
    request: CartUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity
    """
    return CartService.update_cart_item(db, current_user, cart_uuid, request.quantity)

@router.delete("/{cart_uuid}")
async def remove_from_cart(
    cart_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove item from cart
    """
    return CartService.remove_from_cart(db, current_user, cart_uuid)

@router.delete("")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear entire cart
    """
    return CartService.clear_cart(db, current_user)
