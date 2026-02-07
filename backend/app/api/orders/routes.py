from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.orders.schemas import OrderResponse, OrderCreateResponse
from app.api.orders.service import OrderService
from app.core.dependencies import get_current_user
from app.models.user import User
from uuid import UUID
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/create", response_model=OrderCreateResponse)
async def create_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create order from current cart
    """
    return OrderService.create_order(db, current_user)

@router.get("/{order_uuid}", response_model=OrderResponse)
async def get_order(
    order_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details
    """
    return OrderService.get_order(db, order_uuid, current_user)

@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for current user
    """
    return OrderService.get_user_orders(db, current_user)
