from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, Set[int]] = {}
        self.topic_subscribers: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[websocket] = set()
        logger.info(f"🔌 New WebSocket connection: {len(self.active_connections)} total")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            subscribed_topics = self.active_connections[websocket]
            
            # Remove from topic subscriber lists
            for topic_id in subscribed_topics:
                if topic_id in self.topic_subscribers:
                    self.topic_subscribers[topic_id].discard(websocket)
            
            # Remove from active connections
            del self.active_connections[websocket]
            logger.info(f"🔌 WebSocket disconnected: {len(self.active_connections)} remaining")
    
    async def subscribe_user(self, websocket: WebSocket, topics: List[int]):
        """Subscribe a user to specific topics"""
        if websocket not in self.active_connections:
            return
        
        self.active_connections[websocket].update(topics)
        
        for topic_id in topics:
            if topic_id not in self.topic_subscribers:
                self.topic_subscribers[topic_id] = set()
            self.topic_subscribers[topic_id].add(websocket)
        
        logger.info(f"📡 User subscribed to topics: {topics}")
    
    async def unsubscribe_user(self, websocket: WebSocket, topics: List[int]):
        """Unsubscribe a user from specific topics"""
        if websocket not in self.active_connections:
            return
        
        self.active_connections[websocket].difference_update(topics)
        
        for topic_id in topics:
            if topic_id in self.topic_subscribers:
                self.topic_subscribers[topic_id].discard(websocket)
        
        logger.info(f"📡 User unsubscribed from topics: {topics}")
    
    async def broadcast_price_update(self, topic_id: int, price_data: dict):
        """Broadcast price update to all subscribers of a topic"""
        if topic_id not in self.topic_subscribers:
            return
        
        message = {
            "type": "price_update",
            "topic_id": topic_id,
            "data": price_data,
            "timestamp": price_data.get("timestamp")
        }
        
        # Send to all subscribers
        disconnected = set()
        for websocket in self.topic_subscribers[topic_id]:
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except:
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_auction_status(self, status_data: dict):
        """Broadcast auction status to all connected users"""
        message = {
            "type": "auction_status",
            "data": status_data,
            "timestamp": status_data.get("timestamp")
        }
        
        # Send to all active connections
        disconnected = set()
        for websocket in self.active_connections.keys():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except:
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_market_snapshot(self, snapshot_data: dict):
        """Broadcast market snapshot to all connected users"""
        message = {
            "type": "market_snapshot",
            "data": snapshot_data,
            "timestamp": snapshot_data.get("timestamp")
        }
        
        # Send to all active connections
        disconnected = set()
        for websocket in self.active_connections.keys():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except:
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_topic_subscriber_count(self, topic_id: int) -> int:
        """Get the number of subscribers for a specific topic"""
        return len(self.topic_subscribers.get(topic_id, set()))
