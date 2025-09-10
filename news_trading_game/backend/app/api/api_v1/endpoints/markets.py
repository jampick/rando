from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Topic, Category, PriceHistory
from app.models.schemas import TopicResponse, TopicDetail, CategoryResponse, MarketSnapshot, MarketData
from sqlalchemy import func, desc
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all active categories"""
    categories = db.query(Category).filter(Category.is_active == True).all()
    return categories

@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    category_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all active topics, optionally filtered by category"""
    query = db.query(Topic).filter(Topic.is_active == True)
    
    if category_id:
        query = query.filter(Topic.category_id == category_id)
    
    topics = query.limit(limit).all()
    
    # Calculate price change percentages
    for topic in topics:
        if topic.previous_price > 0:
            topic.price_change_percent = ((topic.current_price - topic.previous_price) / topic.previous_price) * 100
        else:
            topic.price_change_percent = 0.0
    
    return topics

@router.get("/topics/{topic_id}", response_model=TopicDetail)
async def get_topic_detail(topic_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get 24h volume and price range
    yesterday = datetime.now() - timedelta(days=1)
    price_history = db.query(PriceHistory).filter(
        PriceHistory.topic_id == topic_id,
        PriceHistory.timestamp >= yesterday
    ).all()
    
    volume_24h = sum(ph.volume for ph in price_history)
    high_24h = max(ph.price for ph in price_history) if price_history else topic.current_price
    low_24h = min(ph.price for ph in price_history) if price_history else topic.current_price
    
    # Calculate price change percentage
    price_change_percent = 0.0
    if topic.previous_price > 0:
        price_change_percent = ((topic.current_price - topic.previous_price) / topic.previous_price) * 100
    
    return TopicDetail(
        id=topic.id,
        name=topic.name,
        ticker=topic.ticker,
        description=topic.description,
        category_id=topic.category_id,
        current_price=topic.current_price,
        previous_price=topic.previous_price,
        price_change_percent=price_change_percent,
        total_shares=topic.total_shares,
        available_shares=topic.available_shares,
        mentions_count=topic.mentions_count,
        fatigue_level=topic.fatigue_level,
        is_active=topic.is_active,
        category=topic.category,
        volume_24h=volume_24h,
        high_24h=high_24h,
        low_24h=low_24h
    )

@router.get("/market-snapshot", response_model=MarketSnapshot)
async def get_market_snapshot(db: Session = Depends(get_db)):
    """Get current market snapshot with all topic data"""
    topics = db.query(Topic).filter(Topic.is_active == True).all()
    
    market_data = []
    for topic in topics:
        price_change_percent = 0.0
        if topic.previous_price > 0:
            price_change_percent = ((topic.current_price - topic.previous_price) / topic.previous_price) * 100
        
        # Get 24h volume
        yesterday = datetime.now() - timedelta(days=1)
        volume_24h = db.query(func.sum(PriceHistory.volume)).filter(
            PriceHistory.topic_id == topic.id,
            PriceHistory.timestamp >= yesterday
        ).scalar() or 0
        
        market_data.append(MarketData(
            topic_id=topic.id,
            ticker=topic.ticker,
            name=topic.name,
            current_price=topic.current_price,
            previous_price=topic.previous_price,
            price_change=topic.current_price - topic.previous_price,
            price_change_percent=price_change_percent,
            volume_24h=volume_24h,
            mentions_count=topic.mentions_count,
            fatigue_level=topic.fatigue_level
        ))
    
    return MarketSnapshot(
        timestamp=datetime.now(),
        topics=market_data
    )

@router.get("/topics/{topic_id}/price-history")
async def get_price_history(
    topic_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get price history for a topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    start_time = datetime.now() - timedelta(hours=hours)
    price_history = db.query(PriceHistory).filter(
        PriceHistory.topic_id == topic_id,
        PriceHistory.timestamp >= start_time
    ).order_by(PriceHistory.timestamp).all()
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "ticker": topic.ticker,
        "price_history": [
            {
                "timestamp": ph.timestamp,
                "price": ph.price,
                "volume": ph.volume,
                "mentions_count": ph.mentions_count
            }
            for ph in price_history
        ]
    }

@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = "daily",  # daily, weekly, all_time
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get leaderboard of top performers"""
    from app.models.models import User, Position
    
    # Calculate time filter
    if timeframe == "daily":
        start_time = datetime.now() - timedelta(days=1)
    elif timeframe == "weekly":
        start_time = datetime.now() - timedelta(weeks=1)
    else:
        start_time = None
    
    # Get users with their total portfolio values
    users = db.query(User).filter(User.is_active == True).all()
    
    leaderboard = []
    for user in users:
        # Calculate total portfolio value
        positions = db.query(Position).filter(Position.user_id == user.id).all()
        
        total_value = user.cash_balance
        total_unrealized_pnl = 0
        
        for position in positions:
            topic = db.query(Topic).filter(Topic.id == position.topic_id).first()
            if topic:
                market_value = position.quantity * topic.current_price
                total_value += market_value
                total_unrealized_pnl += position.unrealized_pnl
        
        leaderboard.append({
            "user_id": user.id,
            "username": user.username,
            "total_value": total_value,
            "cash_balance": user.cash_balance,
            "total_unrealized_pnl": total_unrealized_pnl,
            "return_percent": ((total_value - 10000) / 10000) * 100  # Assuming 10k starting cash
        })
    
    # Sort by total value
    leaderboard.sort(key=lambda x: x["total_value"], reverse=True)
    
    return {
        "timeframe": timeframe,
        "leaderboard": leaderboard[:limit],
        "timestamp": datetime.now()
    }
