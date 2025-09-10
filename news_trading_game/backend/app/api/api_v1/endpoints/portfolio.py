from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, Position, Topic, Trade
from app.models.schemas import PortfolioResponse, PositionResponse, TradeResponse
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Get user's portfolio"""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all positions
    positions = db.query(Position).filter(Position.user_id == user_id).all()
    
    position_responses = []
    total_unrealized_pnl = 0.0
    
    for position in positions:
        topic = db.query(Topic).filter(Topic.id == position.topic_id).first()
        if not topic:
            continue
        
        market_value = position.quantity * topic.current_price
        unrealized_pnl = market_value - (position.quantity * position.average_cost)
        unrealized_pnl_percent = 0.0
        
        if position.quantity != 0 and position.average_cost != 0:
            unrealized_pnl_percent = (unrealized_pnl / (position.quantity * position.average_cost)) * 100
        
        position_responses.append(PositionResponse(
            id=position.id,
            topic_id=position.topic_id,
            topic_name=topic.name,
            topic_ticker=topic.ticker,
            quantity=position.quantity,
            average_cost=position.average_cost,
            current_price=topic.current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_percent=unrealized_pnl_percent
        ))
        
        total_unrealized_pnl += unrealized_pnl
    
    # Calculate total portfolio value
    total_value = user.cash_balance + sum(pos.market_value for pos in position_responses)
    total_unrealized_pnl_percent = 0.0
    
    if total_value > 0:
        total_unrealized_pnl_percent = (total_unrealized_pnl / (total_value - total_unrealized_pnl)) * 100
    
    return PortfolioResponse(
        total_value=total_value,
        cash_balance=user.cash_balance,
        positions=position_responses,
        total_unrealized_pnl=total_unrealized_pnl,
        total_unrealized_pnl_percent=total_unrealized_pnl_percent
    )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Get user's positions"""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all positions
    positions = db.query(Position).filter(Position.user_id == user_id).all()
    
    position_responses = []
    
    for position in positions:
        topic = db.query(Topic).filter(Topic.id == position.topic_id).first()
        if not topic:
            continue
        
        market_value = position.quantity * topic.current_price
        unrealized_pnl = market_value - (position.quantity * position.average_cost)
        unrealized_pnl_percent = 0.0
        
        if position.quantity != 0 and position.average_cost != 0:
            unrealized_pnl_percent = (unrealized_pnl / (position.quantity * position.average_cost)) * 100
        
        position_responses.append(PositionResponse(
            id=position.id,
            topic_id=position.topic_id,
            topic_name=topic.name,
            topic_ticker=topic.ticker,
            quantity=position.quantity,
            average_cost=position.average_cost,
            current_price=topic.current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_percent=unrealized_pnl_percent
        ))
    
    return position_responses

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    user_id: int = 1,  # TODO: Get from authentication
    limit: int = 50,
    topic_id: int = None,
    db: Session = Depends(get_db)
):
    """Get user's trade history"""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(Trade).filter(Trade.user_id == user_id)
    
    if topic_id:
        query = query.filter(Trade.topic_id == topic_id)
    
    trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    trade_responses = []
    
    for trade in trades:
        topic = db.query(Topic).filter(Topic.id == trade.topic_id).first()
        if not topic:
            continue
        
        trade_responses.append(TradeResponse(
            id=trade.id,
            topic_id=trade.topic_id,
            topic_name=topic.name,
            topic_ticker=topic.ticker,
            order_type=trade.order_type,
            quantity=trade.quantity,
            price=trade.price,
            realized_pnl=trade.realized_pnl,
            auction_id=trade.auction_id,
            created_at=trade.created_at
        ))
    
    return trade_responses

@router.get("/performance")
async def get_performance(
    user_id: int = 1,  # TODO: Get from authentication
    timeframe: str = "daily",  # daily, weekly, monthly, all_time
    db: Session = Depends(get_db)
):
    """Get user's performance metrics"""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate time filter
    if timeframe == "daily":
        start_time = datetime.now() - timedelta(days=1)
    elif timeframe == "weekly":
        start_time = datetime.now() - timedelta(weeks=1)
    elif timeframe == "monthly":
        start_time = datetime.now() - timedelta(days=30)
    else:
        start_time = None
    
    # Get trades in timeframe
    query = db.query(Trade).filter(Trade.user_id == user_id)
    if start_time:
        query = query.filter(Trade.created_at >= start_time)
    
    trades = query.all()
    
    # Calculate metrics
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.realized_pnl > 0])
    losing_trades = len([t for t in trades if t.realized_pnl < 0])
    
    total_realized_pnl = sum(t.realized_pnl for t in trades)
    total_volume = sum(abs(t.quantity * t.price) for t in trades)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Get current portfolio value
    positions = db.query(Position).filter(Position.user_id == user_id).all()
    current_portfolio_value = user.cash_balance
    
    for position in positions:
        topic = db.query(Topic).filter(Topic.id == position.topic_id).first()
        if topic:
            current_portfolio_value += position.quantity * topic.current_price
    
    # Calculate return percentage
    initial_cash = 10000.0  # Assuming 10k starting cash
    total_return_percent = ((current_portfolio_value - initial_cash) / initial_cash) * 100
    
    return {
        "user_id": user_id,
        "timeframe": timeframe,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "total_realized_pnl": total_realized_pnl,
        "total_volume": total_volume,
        "current_portfolio_value": current_portfolio_value,
        "total_return_percent": total_return_percent,
        "timestamp": datetime.now()
    }
