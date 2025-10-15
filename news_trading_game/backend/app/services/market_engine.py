import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from app.core.database import SessionLocal
from app.models.models import (
    Topic, Category, Order, Trade, Position, Auction, User, PriceHistory,
    OrderType, OrderStatus, CategoryType
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class MarketEngine:
    def __init__(self):
        self.is_running = False
        self.current_auction_id = None
        self.next_auction_time = None
        self.price_cache = {}
        
    async def start_auction_scheduler(self):
        """Start the batch auction scheduler"""
        self.is_running = True
        logger.info("🚀 Starting batch auction scheduler...")
        
        while self.is_running:
            try:
                await self._schedule_next_auction()
                await self._wait_for_auction_time()
                await self._run_auction()
            except Exception as e:
                logger.error(f"Error in auction scheduler: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def start_price_updater(self):
        """Start the price update service"""
        logger.info("📈 Starting price update service...")
        
        while self.is_running:
            try:
                await self._update_prices()
                await asyncio.sleep(settings.price_update_interval_seconds)
            except Exception as e:
                logger.error(f"Error in price updater: {e}")
                await asyncio.sleep(30)
    
    async def _schedule_next_auction(self):
        """Schedule the next auction with randomization"""
        db = SessionLocal()
        try:
            # Calculate next auction time with randomization
            base_interval = timedelta(minutes=settings.auction_interval_minutes)
            randomization = timedelta(seconds=random.randint(
                -settings.auction_randomization_seconds,
                settings.auction_randomization_seconds
            ))
            
            self.next_auction_time = datetime.now() + base_interval + randomization
            
            # Create auction record
            auction_number = await self._get_next_auction_number(db)
            auction = Auction(
                auction_number=auction_number,
                scheduled_time=self.next_auction_time,
                status="scheduled"
            )
            db.add(auction)
            db.commit()
            
            self.current_auction_id = auction.id
            logger.info(f"📅 Scheduled auction #{auction_number} for {self.next_auction_time}")
            
        finally:
            db.close()
    
    async def _wait_for_auction_time(self):
        """Wait until it's time for the auction"""
        if not self.next_auction_time:
            return
            
        wait_time = (self.next_auction_time - datetime.now()).total_seconds()
        if wait_time > 0:
            logger.info(f"⏰ Waiting {wait_time:.0f} seconds for next auction...")
            await asyncio.sleep(wait_time)
    
    async def _run_auction(self):
        """Execute a batch auction"""
        if not self.current_auction_id:
            return
            
        db = SessionLocal()
        try:
            logger.info(f"🔨 Running auction #{self.current_auction_id}")
            
            # Update auction status
            auction = db.query(Auction).filter(Auction.id == self.current_auction_id).first()
            if auction:
                auction.status = "running"
                auction.actual_time = datetime.now()
                db.commit()
            
            # Process orders for each topic
            topics = db.query(Topic).filter(Topic.is_active == True).all()
            
            for topic in topics:
                await self._process_topic_auction(db, topic)
            
            # Update auction completion
            if auction:
                auction.status = "completed"
                auction.completed_at = datetime.now()
                db.commit()
            
            logger.info(f"✅ Completed auction #{self.current_auction_id}")
            
        except Exception as e:
            logger.error(f"Error running auction: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _process_topic_auction(self, db: Session, topic: Topic):
        """Process all orders for a specific topic in the auction"""
        # Get all pending orders for this topic
        orders = db.query(Order).filter(
            Order.topic_id == topic.id,
            Order.status == OrderStatus.PENDING
        ).all()
        
        if not orders:
            return
        
        # Separate orders by type
        buy_orders = [o for o in orders if o.order_type == OrderType.BUY]
        sell_orders = [o for o in orders if o.order_type == OrderType.SELL]
        short_orders = [o for o in orders if o.order_type == OrderType.SHORT]
        
        # Calculate clearing price using zero-sum mechanics
        clearing_price = await self._calculate_clearing_price(
            db, topic, buy_orders, sell_orders, short_orders
        )
        
        # Execute trades at clearing price
        await self._execute_trades(
            db, topic, clearing_price, buy_orders, sell_orders, short_orders
        )
        
        # Update topic price
        topic.previous_price = topic.current_price
        topic.current_price = clearing_price
        db.commit()
    
    async def _calculate_clearing_price(
        self, 
        db: Session, 
        topic: Topic, 
        buy_orders: List[Order], 
        sell_orders: List[Order], 
        short_orders: List[Order]
    ) -> float:
        """Calculate the clearing price using zero-sum mechanics"""
        
        # Get current attention metrics
        total_mentions_in_category = db.query(func.sum(Topic.mentions_count)).filter(
            Topic.category_id == topic.category_id,
            Topic.is_active == True
        ).scalar() or 1
        
        # Calculate attention ratio
        attention_ratio = topic.mentions_count / total_mentions_in_category
        
        # Get category market cap
        category = db.query(Category).filter(Category.id == topic.category_id).first()
        market_cap = category.market_cap if category else 1000000.0
        
        # Base price calculation
        base_price = attention_ratio * market_cap / topic.total_shares
        
        # Apply fatigue correction if topic is dominating
        if topic.fatigue_level > 0.7:  # High fatigue threshold
            fatigue_correction = 1.0 - (topic.fatigue_level - 0.7) * 0.5
            base_price *= fatigue_correction
        
        # Apply order flow pressure
        total_buy_volume = sum(o.quantity for o in buy_orders)
        total_sell_volume = sum(o.quantity for o in sell_orders + short_orders)
        
        if total_buy_volume > total_sell_volume:
            # Buy pressure - price goes up
            pressure_multiplier = 1.0 + min(0.1, (total_buy_volume - total_sell_volume) / topic.total_shares)
        else:
            # Sell pressure - price goes down
            pressure_multiplier = 1.0 - min(0.1, (total_sell_volume - total_buy_volume) / topic.total_shares)
        
        clearing_price = base_price * pressure_multiplier
        
        # Ensure minimum price
        return max(0.01, clearing_price)
    
    async def _execute_trades(
        self,
        db: Session,
        topic: Topic,
        clearing_price: float,
        buy_orders: List[Order],
        sell_orders: List[Order],
        short_orders: List[Order]
    ):
        """Execute all trades at the clearing price"""
        
        # Process buy orders
        for order in buy_orders:
            await self._fill_buy_order(db, order, clearing_price)
        
        # Process sell orders
        for order in sell_orders:
            await self._fill_sell_order(db, order, clearing_price)
        
        # Process short orders
        for order in short_orders:
            await self._fill_short_order(db, order, clearing_price)
    
    async def _fill_buy_order(self, db: Session, order: Order, price: float):
        """Fill a buy order"""
        user = db.query(User).filter(User.id == order.user_id).first()
        if not user or user.cash_balance < order.quantity * price:
            order.status = OrderStatus.CANCELLED
            db.commit()
            return
        
        # Execute the trade
        trade = Trade(
            user_id=order.user_id,
            topic_id=order.topic_id,
            order_type=OrderType.BUY,
            quantity=order.quantity,
            price=price,
            auction_id=self.current_auction_id
        )
        db.add(trade)
        
        # Update user cash
        user.cash_balance -= order.quantity * price
        
        # Update position
        await self._update_position(db, order.user_id, order.topic_id, order.quantity, price)
        
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = price
        
        db.commit()
    
    async def _fill_sell_order(self, db: Session, order: Order, price: float):
        """Fill a sell order"""
        # Check if user has enough shares
        position = db.query(Position).filter(
            Position.user_id == order.user_id,
            Position.topic_id == order.topic_id
        ).first()
        
        if not position or position.quantity < order.quantity:
            order.status = OrderStatus.CANCELLED
            db.commit()
            return
        
        # Execute the trade
        trade = Trade(
            user_id=order.user_id,
            topic_id=order.topic_id,
            order_type=OrderType.SELL,
            quantity=order.quantity,
            price=price,
            auction_id=self.current_auction_id,
            realized_pnl=(price - position.average_cost) * order.quantity
        )
        db.add(trade)
        
        # Update user cash
        user = db.query(User).filter(User.id == order.user_id).first()
        user.cash_balance += order.quantity * price
        
        # Update position
        await self._update_position(db, order.user_id, order.topic_id, -order.quantity, price)
        
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = price
        
        db.commit()
    
    async def _fill_short_order(self, db: Session, order: Order, price: float):
        """Fill a short order"""
        # Check short selling limits (max 20% of float)
        max_short_shares = int(topic.total_shares * 0.2)
        current_short_positions = db.query(func.sum(Position.quantity)).filter(
            Position.topic_id == order.topic_id,
            Position.quantity < 0
        ).scalar() or 0
        
        if abs(current_short_positions) + order.quantity > max_short_shares:
            order.status = OrderStatus.CANCELLED
            db.commit()
            return
        
        # Execute the trade
        trade = Trade(
            user_id=order.user_id,
            topic_id=order.topic_id,
            order_type=OrderType.SHORT,
            quantity=order.quantity,
            price=price,
            auction_id=self.current_auction_id
        )
        db.add(trade)
        
        # Update user cash (short sale proceeds)
        user = db.query(User).filter(User.id == order.user_id).first()
        user.cash_balance += order.quantity * price
        
        # Update position (negative quantity for short)
        await self._update_position(db, order.user_id, order.topic_id, -order.quantity, price)
        
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = price
        
        db.commit()
    
    async def _update_position(self, db: Session, user_id: int, topic_id: int, quantity_change: int, price: float):
        """Update user's position after a trade"""
        position = db.query(Position).filter(
            Position.user_id == user_id,
            Position.topic_id == topic_id
        ).first()
        
        if not position:
            position = Position(
                user_id=user_id,
                topic_id=topic_id,
                quantity=0,
                average_cost=0.0
            )
            db.add(position)
        
        # Update average cost
        if position.quantity + quantity_change == 0:
            position.average_cost = 0.0
        elif position.quantity + quantity_change > 0:
            # Long position
            total_cost = (position.quantity * position.average_cost) + (quantity_change * price)
            position.average_cost = total_cost / (position.quantity + quantity_change)
        else:
            # Short position - average cost is the price we shorted at
            position.average_cost = price
        
        position.quantity += quantity_change
        db.commit()
    
    async def _update_prices(self):
        """Update prices based on current attention metrics and market dynamics"""
        db = SessionLocal()
        try:
            topics = db.query(Topic).filter(Topic.is_active == True).all()
            
            for topic in topics:
                # Calculate price change based on mention dynamics
                price_change = await self._calculate_price_change(db, topic)
                
                # Apply the price change
                new_price = topic.current_price * (1 + price_change)
                topic.current_price = max(0.01, new_price)
                
                # Record price history
                await self._record_price_history(db, topic)
            
            db.commit()
            
        finally:
            db.close()
    
    async def _calculate_price_change(self, db: Session, topic: Topic) -> float:
        """Calculate realistic price changes based on market dynamics"""
        
        # Get recent mention trend (last 5 minutes)
        recent_mentions = topic.mentions_count
        
        # Calculate attention ratio within category
        total_category_mentions = db.query(func.sum(Topic.mentions_count)).filter(
            Topic.category_id == topic.category_id,
            Topic.is_active == True
        ).scalar() or 1
        
        attention_ratio = recent_mentions / total_category_mentions
        
        # Base price change from attention
        base_change = (attention_ratio - 0.1) * 0.05  # Scale attention to price change
        
        # Add volatility based on topic type
        volatility = self._get_topic_volatility(topic)
        
        # Add random market noise
        noise = random.gauss(0, volatility * 0.01)
        
        # Apply momentum effects
        momentum = self._calculate_momentum(db, topic)
        
        # Combine all factors
        total_change = base_change + noise + momentum
        
        # Cap extreme movements
        total_change = max(-0.15, min(0.15, total_change))  # ±15% max
        
        return total_change
    
    def _get_topic_volatility(self, topic: Topic) -> float:
        """Get volatility multiplier based on topic characteristics"""
        if 'Crypto' in topic.name:
            return 2.0  # High volatility
        elif 'AI' in topic.name or 'Tech' in topic.name:
            return 1.5  # Medium-high volatility
        elif 'Policy' in topic.name or 'Climate' in topic.name:
            return 1.2  # Medium volatility
        else:
            return 1.0  # Normal volatility
    
    def _calculate_momentum(self, db: Session, topic: Topic) -> float:
        """Calculate momentum effect based on recent price history"""
        # Get recent price history (last 3 records)
        recent_history = db.query(PriceHistory).filter(
            PriceHistory.topic_id == topic.id
        ).order_by(PriceHistory.timestamp.desc()).limit(3).all()
        
        if len(recent_history) < 2:
            return 0.0
        
        # Calculate recent trend
        recent_changes = []
        for i in range(1, len(recent_history)):
            change = (recent_history[i-1].price - recent_history[i].price) / recent_history[i].price
            recent_changes.append(change)
        
        # Momentum effect (trend continuation)
        avg_change = sum(recent_changes) / len(recent_changes)
        momentum = avg_change * 0.3  # 30% momentum effect
        
        return momentum
    
    async def _record_price_history(self, db: Session, topic: Topic):
        """Record price history for the topic"""
        # Only record every 2 minutes to avoid too much data
        last_record = db.query(PriceHistory).filter(
            PriceHistory.topic_id == topic.id
        ).order_by(PriceHistory.timestamp.desc()).first()
        
        if not last_record or (datetime.now() - last_record.timestamp).total_seconds() > 120:
            price_history = PriceHistory(
                topic_id=topic.id,
                price=topic.current_price,
                volume=random.randint(100, 1000),  # Simulated volume
                mentions_count=topic.mentions_count
            )
            db.add(price_history)
    
    async def _get_next_auction_number(self, db: Session) -> int:
        """Get the next auction number"""
        last_auction = db.query(Auction).order_by(desc(Auction.auction_number)).first()
        return (last_auction.auction_number + 1) if last_auction else 1
    
    def get_current_time(self) -> datetime:
        """Get current time for health checks"""
        return datetime.now()
    
    def stop(self):
        """Stop the market engine"""
        self.is_running = False
        logger.info("🛑 Market engine stopped")
