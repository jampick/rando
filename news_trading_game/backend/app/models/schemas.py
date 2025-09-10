from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.models import OrderType, OrderStatus, CategoryType

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    cash_balance: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category schemas
class CategoryResponse(BaseModel):
    id: int
    name: CategoryType
    display_name: str
    market_cap: float
    is_active: bool
    
    class Config:
        from_attributes = True

# Topic schemas
class TopicBase(BaseModel):
    name: str
    ticker: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    category_id: int

class TopicResponse(TopicBase):
    id: int
    category_id: int
    current_price: float
    previous_price: float
    price_change_percent: float
    total_shares: int
    available_shares: int
    mentions_count: int
    fatigue_level: float
    is_active: bool
    
    class Config:
        from_attributes = True

class TopicDetail(TopicResponse):
    category: CategoryResponse
    volume_24h: int
    high_24h: float
    low_24h: float
    
    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    topic_id: int
    order_type: OrderType
    quantity: int = Field(..., gt=0)
    price_limit: Optional[float] = Field(None, gt=0)

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    filled_quantity: int
    average_fill_price: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Position schemas
class PositionResponse(BaseModel):
    id: int
    topic_id: int
    topic_name: str
    topic_ticker: str
    quantity: int
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    
    class Config:
        from_attributes = True

# Trade schemas
class TradeResponse(BaseModel):
    id: int
    topic_id: int
    topic_name: str
    topic_ticker: str
    order_type: OrderType
    quantity: int
    price: float
    realized_pnl: float
    auction_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Portfolio schemas
class PortfolioResponse(BaseModel):
    total_value: float
    cash_balance: float
    positions: List[PositionResponse]
    total_unrealized_pnl: float
    total_unrealized_pnl_percent: float

# Market data schemas
class MarketData(BaseModel):
    topic_id: int
    ticker: str
    name: str
    current_price: float
    previous_price: float
    price_change: float
    price_change_percent: float
    volume_24h: int
    mentions_count: int
    fatigue_level: float

class MarketSnapshot(BaseModel):
    timestamp: datetime
    topics: List[MarketData]

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.now)

class PriceUpdateMessage(BaseModel):
    type: str = "price_update"
    topic_id: int
    ticker: str
    price: float
    change_percent: float
    volume: int
    timestamp: datetime = Field(default_factory=datetime.now)

class AuctionStatusMessage(BaseModel):
    type: str = "auction_status"
    status: str  # "scheduled", "running", "completed"
    next_auction_time: Optional[datetime]
    current_auction_id: Optional[int]
    timestamp: datetime = Field(default_factory=datetime.now)
