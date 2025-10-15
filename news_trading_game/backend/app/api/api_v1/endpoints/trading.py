from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Order, OrderType, OrderStatus, User, Topic
from app.models.schemas import OrderCreate, OrderResponse
from datetime import datetime

router = APIRouter()

@router.post("/test")
async def test_endpoint():
    """Test endpoint to debug issues"""
    return {"message": "Trading endpoint is working", "status": "ok"}

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Create a new trading order"""
    
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate topic exists
        topic = db.query(Topic).filter(Topic.id == order_data.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    
    try:
        # Validate order constraints
        if order_data.order_type == OrderType.BUY:
            # Check if user has enough cash
            required_cash = order_data.quantity * (order_data.price_limit or topic.current_price)
            if user.cash_balance < required_cash:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient cash. Required: ${required_cash:.2f}, Available: ${user.cash_balance:.2f}"
                )
        
        elif order_data.order_type == OrderType.SELL:
            # Check if user has enough shares
            from app.models.models import Position
            position = db.query(Position).filter(
                Position.user_id == user_id,
                Position.topic_id == order_data.topic_id
            ).first()
            
            if not position or position.quantity < order_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient shares. Required: {order_data.quantity}, Available: {position.quantity if position else 0}"
                )
        
        elif order_data.order_type == OrderType.SHORT:
            # Check short selling limits (max 20% of float)
            max_short_shares = int(topic.total_shares * 0.2)
            from app.models.models import Position
            current_short_positions = db.query(Position).filter(
                Position.topic_id == order_data.topic_id,
                Position.quantity < 0
            ).all()
            
            total_short = sum(abs(pos.quantity) for pos in current_short_positions)
            if total_short + order_data.quantity > max_short_shares:
                raise HTTPException(
                    status_code=400,
                    detail=f"Short selling limit exceeded. Max: {max_short_shares}, Current: {total_short}, Requested: {order_data.quantity}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order validation error: {str(e)}")
    
    # Create the order
    try:
        order = Order(
            user_id=user_id,
            topic_id=order_data.topic_id,
            order_type=order_data.order_type,
            quantity=order_data.quantity,
            price_limit=order_data.price_limit,
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    user_id: int = 1,  # TODO: Get from authentication
    status: OrderStatus = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).limit(limit).all()
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Get a specific order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: int,
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Cancel a pending order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id,
        Order.status == OrderStatus.PENDING
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or cannot be cancelled")
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    
    return {"message": "Order cancelled successfully"}

@router.get("/order-book/{topic_id}")
async def get_order_book(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """Get the order book for a specific topic"""
    
    # Validate topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get pending orders
    buy_orders = db.query(Order).filter(
        Order.topic_id == topic_id,
        Order.order_type == OrderType.BUY,
        Order.status == OrderStatus.PENDING
    ).order_by(Order.price_limit.desc()).all()
    
    sell_orders = db.query(Order).filter(
        Order.topic_id == topic_id,
        Order.order_type.in_([OrderType.SELL, OrderType.SHORT]),
        Order.status == OrderStatus.PENDING
    ).order_by(Order.price_limit.asc()).all()
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "ticker": topic.ticker,
        "current_price": topic.current_price,
        "buy_orders": [
            {
                "id": order.id,
                "quantity": order.quantity,
                "price_limit": order.price_limit,
                "created_at": order.created_at
            }
            for order in buy_orders
        ],
        "sell_orders": [
            {
                "id": order.id,
                "quantity": order.quantity,
                "price_limit": order.price_limit,
                "order_type": order.order_type,
                "created_at": order.created_at
            }
            for order in sell_orders
        ],
        "timestamp": datetime.now()
    }

@router.get("/recent-trades/{topic_id}")
async def get_recent_trades(
    topic_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent trades for a specific topic"""
    
    # Validate topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    from app.models.models import Trade
    trades = db.query(Trade).filter(
        Trade.topic_id == topic_id
    ).order_by(Trade.created_at.desc()).limit(limit).all()
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "ticker": topic.ticker,
        "recent_trades": [
            {
                "id": trade.id,
                "order_type": trade.order_type,
                "quantity": trade.quantity,
                "price": trade.price,
                "auction_id": trade.auction_id,
                "created_at": trade.created_at
            }
            for trade in trades
        ],
        "timestamp": datetime.now()
    }
