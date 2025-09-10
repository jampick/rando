from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
from typing import Optional

class CategoryType(str, enum.Enum):
    POLITICS = "politics"
    TECH = "tech"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"

class OrderType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    PARTIALLY_FILLED = "partially_filled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    cash_balance = Column(Float, default=10000.0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    positions = relationship("Position", back_populates="user")
    trades = relationship("Trade", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(CategoryType), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    market_cap = Column(Float, default=1000000.0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topics = relationship("Topic", back_populates="category")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text)
    
    # Market data
    current_price = Column(Float, default=0.0)
    previous_price = Column(Float, default=0.0)
    total_shares = Column(Integer, default=1000000)
    available_shares = Column(Integer, default=1000000)
    
    # Attention metrics
    mentions_count = Column(Integer, default=0)
    last_mention_time = Column(DateTime(timezone=True))
    
    # Fatigue tracking
    fatigue_level = Column(Float, default=0.0)  # 0-1 scale
    dominance_start_time = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="topics")
    orders = relationship("Order", back_populates="topic")
    positions = relationship("Position", back_populates="topic")
    trades = relationship("Trade", back_populates="topic")
    price_history = relationship("PriceHistory", back_populates="topic")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_limit = Column(Float)  # None for market orders
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    filled_quantity = Column(Integer, default=0)
    average_fill_price = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    topic = relationship("Topic", back_populates="orders")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    quantity = Column(Integer, default=0)  # Can be negative for short positions
    average_cost = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="positions")
    topic = relationship("Topic", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    realized_pnl = Column(Float, default=0.0)
    
    auction_id = Column(Integer, nullable=False)  # Which auction this trade occurred in
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trades")
    topic = relationship("Topic", back_populates="trades")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    price = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    mentions_count = Column(Integer, default=0)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="price_history")

class Auction(Base):
    __tablename__ = "auctions"
    
    id = Column(Integer, primary_key=True, index=True)
    auction_number = Column(Integer, unique=True, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    actual_time = Column(DateTime(timezone=True))
    
    total_orders = Column(Integer, default=0)
    total_volume = Column(Integer, default=0)
    status = Column(String(20), default="scheduled")  # scheduled, running, completed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
