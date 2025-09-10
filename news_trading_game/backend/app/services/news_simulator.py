import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Topic, Category, PriceHistory, CategoryType
import logging

logger = logging.getLogger(__name__)

class NewsSimulator:
    def __init__(self):
        self.is_running = False
        self.topic_mentions = {}
        self.trending_topics = set()
        
    async def start_simulation(self):
        """Start the news mention simulation"""
        self.is_running = True
        logger.info("📰 Starting news mention simulation...")
        
        # Initialize topic mentions
        await self._initialize_topic_mentions()
        
        while self.is_running:
            try:
                await self._simulate_news_cycle()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in news simulation: {e}")
                await asyncio.sleep(30)
    
    async def _initialize_topic_mentions(self):
        """Initialize mention counts for all topics"""
        db = SessionLocal()
        try:
            topics = db.query(Topic).filter(Topic.is_active == True).all()
            
            for topic in topics:
                # Start with random baseline mentions
                baseline_mentions = random.randint(10, 100)
                self.topic_mentions[topic.id] = baseline_mentions
                topic.mentions_count = baseline_mentions
                
                # Randomly select some topics to be trending
                if random.random() < 0.3:  # 30% chance to be trending
                    self.trending_topics.add(topic.id)
            
            db.commit()
            logger.info(f"📊 Initialized {len(topics)} topics with baseline mentions")
            
        finally:
            db.close()
    
    async def _simulate_news_cycle(self):
        """Simulate one cycle of news mentions"""
        db = SessionLocal()
        try:
            topics = db.query(Topic).filter(Topic.is_active == True).all()
            
            for topic in topics:
                await self._update_topic_mentions(db, topic)
            
            db.commit()
            
        finally:
            db.close()
    
    async def _update_topic_mentions(self, db: Session, topic: Topic):
        """Update mentions for a specific topic with realistic market dynamics"""
        current_mentions = self.topic_mentions.get(topic.id, 0)
        
        # Base mention rate varies by topic type
        base_rate = self._get_base_rate_for_topic(topic)
        
        # Trending topics get more mentions
        if topic.id in self.trending_topics:
            base_rate *= random.uniform(2.5, 4.0)
        
        # Add realistic randomness with market cycles
        mention_change = self._calculate_mention_change(base_rate, topic)
        
        # Create different types of market events
        event_type = self._determine_market_event()
        if event_type:
            mention_change = self._apply_market_event(mention_change, event_type, topic)
        
        # Update mentions
        new_mentions = max(0, current_mentions + mention_change)
        self.topic_mentions[topic.id] = new_mentions
        topic.mentions_count = new_mentions
        topic.last_mention_time = datetime.now()
        
        # Update fatigue level
        await self._update_fatigue_level(db, topic)
        
        # Record price history
        await self._record_price_history(db, topic)
    
    def _get_base_rate_for_topic(self, topic: Topic) -> float:
        """Get base mention rate based on topic characteristics"""
        # Different topics have different baseline attention
        if 'AI' in topic.name or 'Tech' in topic.name:
            return random.uniform(0.8, 1.2)  # Higher baseline for tech
        elif 'Climate' in topic.name or 'Policy' in topic.name:
            return random.uniform(0.6, 1.0)  # Medium baseline for policy
        elif 'Crypto' in topic.name or 'Space' in topic.name:
            return random.uniform(0.4, 0.8)  # Lower baseline but more volatile
        else:
            return random.uniform(0.3, 0.7)  # Default baseline
    
    def _calculate_mention_change(self, base_rate: float, topic: Topic) -> int:
        """Calculate realistic mention changes"""
        # Use normal distribution for more realistic changes
        change = random.gauss(base_rate, base_rate * 0.3)
        
        # Add time-based patterns (more activity during "business hours")
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            change *= random.uniform(1.2, 1.5)
        elif 18 <= hour <= 22:  # Evening news
            change *= random.uniform(1.1, 1.3)
        else:  # Night/early morning
            change *= random.uniform(0.7, 1.0)
        
        return max(0, int(change))
    
    def _determine_market_event(self) -> str:
        """Determine if a special market event should occur"""
        rand = random.random()
        
        if rand < 0.02:  # 2% chance
            return 'viral_spike'
        elif rand < 0.03:  # 1% chance
            return 'news_break'
        elif rand < 0.05:  # 2% chance
            return 'correction'
        elif rand < 0.08:  # 3% chance
            return 'momentum'
        else:
            return None
    
    def _apply_market_event(self, base_change: int, event_type: str, topic: Topic) -> int:
        """Apply special market events"""
        if event_type == 'viral_spike':
            multiplier = random.uniform(3.0, 8.0)
            logger.info(f"🔥 VIRAL SPIKE: {topic.name} +{int(base_change * multiplier)} mentions")
            return int(base_change * multiplier)
        
        elif event_type == 'news_break':
            multiplier = random.uniform(2.0, 4.0)
            logger.info(f"📰 NEWS BREAK: {topic.name} +{int(base_change * multiplier)} mentions")
            return int(base_change * multiplier)
        
        elif event_type == 'correction':
            # Negative change for corrections
            multiplier = random.uniform(-0.8, -0.3)
            logger.info(f"📉 CORRECTION: {topic.name} {int(base_change * multiplier)} mentions")
            return int(base_change * multiplier)
        
        elif event_type == 'momentum':
            multiplier = random.uniform(1.5, 2.5)
            logger.info(f"⚡ MOMENTUM: {topic.name} +{int(base_change * multiplier)} mentions")
            return int(base_change * multiplier)
        
        return base_change
    
    async def _update_fatigue_level(self, db: Session, topic: Topic):
        """Update fatigue level based on dominance"""
        # Get total mentions in category
        total_category_mentions = db.query(Topic).filter(
            Topic.category_id == topic.category_id,
            Topic.is_active == True
        ).with_entities(Topic.mentions_count).all()
        
        total_mentions = sum(t.mentions_count for t in total_category_mentions)
        
        if total_mentions > 0:
            dominance_ratio = topic.mentions_count / total_mentions
            
            # Update fatigue based on dominance
            if dominance_ratio > 0.5:  # Dominating
                if not topic.dominance_start_time:
                    topic.dominance_start_time = datetime.now()
                
                # Increase fatigue over time
                dominance_duration = datetime.now() - topic.dominance_start_time
                fatigue_increase = min(0.1, dominance_duration.total_seconds() / 3600 * 0.01)  # Max 0.1 per hour
                topic.fatigue_level = min(1.0, topic.fatigue_level + fatigue_increase)
                
            else:  # Not dominating
                topic.dominance_start_time = None
                # Decrease fatigue over time
                topic.fatigue_level = max(0.0, topic.fatigue_level - 0.01)
            
            # Randomly reset trending status
            if topic.id in self.trending_topics and random.random() < 0.1:
                self.trending_topics.discard(topic.id)
                logger.info(f"📉 {topic.name} is no longer trending")
            
            # Randomly make topics trending
            elif topic.id not in self.trending_topics and random.random() < 0.05:
                self.trending_topics.add(topic.id)
                logger.info(f"📈 {topic.name} is now trending")
    
    async def _record_price_history(self, db: Session, topic: Topic):
        """Record price history for the topic"""
        # Only record every 5 minutes to avoid too much data
        last_record = db.query(PriceHistory).filter(
            PriceHistory.topic_id == topic.id
        ).order_by(PriceHistory.timestamp.desc()).first()
        
        if not last_record or (datetime.now() - last_record.timestamp).total_seconds() > 300:
            price_history = PriceHistory(
                topic_id=topic.id,
                price=topic.current_price,
                volume=random.randint(100, 1000),  # Simulated volume
                mentions_count=topic.mentions_count
            )
            db.add(price_history)
    
    def get_topic_mentions(self, topic_id: int) -> int:
        """Get current mention count for a topic"""
        return self.topic_mentions.get(topic_id, 0)
    
    def get_trending_topics(self) -> List[int]:
        """Get list of currently trending topic IDs"""
        return list(self.trending_topics)
    
    def stop(self):
        """Stop the simulation"""
        self.is_running = False
        logger.info("🛑 News simulation stopped")

# Sample data for MVP
SAMPLE_CATEGORIES = [
    {"name": CategoryType.POLITICS, "display_name": "Politics", "market_cap": 2000000.0},
    {"name": CategoryType.TECH, "display_name": "Technology", "market_cap": 3000000.0},
]

SAMPLE_TOPICS = [
    # Politics
    {"name": "AI Regulation", "ticker": "AIR", "category": CategoryType.POLITICS, "description": "Government policies on artificial intelligence"},
    {"name": "Climate Policy", "ticker": "CLP", "category": CategoryType.POLITICS, "description": "Environmental legislation and climate change policies"},
    {"name": "Healthcare Reform", "ticker": "HCR", "category": CategoryType.POLITICS, "description": "Healthcare system changes and reforms"},
    {"name": "Immigration Policy", "ticker": "IMP", "category": CategoryType.POLITICS, "description": "Immigration laws and border policies"},
    {"name": "Tax Reform", "ticker": "TXR", "category": CategoryType.POLITICS, "description": "Taxation policy changes"},
    
    # Technology
    {"name": "Cryptocurrency", "ticker": "CRY", "category": CategoryType.TECH, "description": "Digital currencies and blockchain technology"},
    {"name": "Electric Vehicles", "ticker": "EVS", "category": CategoryType.TECH, "description": "Electric vehicle technology and adoption"},
    {"name": "Space Exploration", "ticker": "SPX", "category": CategoryType.TECH, "description": "Space missions and exploration technology"},
    {"name": "Quantum Computing", "ticker": "QTC", "category": CategoryType.TECH, "description": "Quantum computing advances and applications"},
    {"name": "Social Media", "ticker": "SOM", "category": CategoryType.TECH, "description": "Social media platforms and policies"},
]

async def initialize_sample_data():
    """Initialize the database with sample data"""
    db = SessionLocal()
    try:
        logger.info("🗄️ Initializing sample data...")
        
        # Create categories
        category_map = {}
        for cat_data in SAMPLE_CATEGORIES:
            # Check if category already exists
            existing_category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if existing_category:
                category_map[cat_data["name"]] = existing_category.id
                continue
                
            category = Category(
                name=cat_data["name"],
                display_name=cat_data["display_name"],
                market_cap=cat_data["market_cap"]
            )
            db.add(category)
            db.flush()  # Get the ID
            category_map[cat_data["name"]] = category.id
        
        # Create topics
        for topic_data in SAMPLE_TOPICS:
            category_id = category_map[topic_data["category"]]
            
            # Check if topic already exists
            existing_topic = db.query(Topic).filter(Topic.ticker == topic_data["ticker"]).first()
            if existing_topic:
                continue
            
            # Set initial price based on category market cap
            category_market_cap = next(cat["market_cap"] for cat in SAMPLE_CATEGORIES if cat["name"] == topic_data["category"])
            initial_price = (category_market_cap / len([t for t in SAMPLE_TOPICS if t["category"] == topic_data["category"]])) / 1000000
            
            topic = Topic(
                name=topic_data["name"],
                ticker=topic_data["ticker"],
                category_id=category_id,
                description=topic_data["description"],
                current_price=initial_price,
                previous_price=initial_price,
                total_shares=1000000,
                available_shares=1000000,
                mentions_count=random.randint(10, 100)
            )
            db.add(topic)
        
        # Create a default user for testing
        from app.models.models import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        existing_user = db.query(User).filter(User.username == "trader").first()
        if not existing_user:
            user = User(
                username="trader",
                email="trader@example.com",
                hashed_password=pwd_context.hash("password123"),
                cash_balance=10000.0
            )
            db.add(user)
            logger.info("👤 Created default user: trader/password123")
        
        db.commit()
        logger.info("✅ Sample data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()
