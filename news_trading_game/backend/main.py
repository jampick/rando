from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, List
import json

from app.core.config import settings
from app.core.database import engine, Base
from app.api.api_v1.api import api_router
from app.services.market_engine import MarketEngine
from app.services.websocket_manager import WebSocketManager

# Create database tables
Base.metadata.create_all(bind=engine)

# Global instances
market_engine = MarketEngine()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting News Trading Game MVP...")
    
    # Start market engine background tasks
    asyncio.create_task(market_engine.start_auction_scheduler())
    asyncio.create_task(market_engine.start_price_updater())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down News Trading Game MVP...")

app = FastAPI(
    title="News Trading Game API",
    description="MVP for news-based trading simulation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "📰 News Trading Game MVP",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": market_engine.get_current_time()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                await websocket_manager.subscribe_user(websocket, message.get("topics", []))
            elif message.get("type") == "unsubscribe":
                await websocket_manager.unsubscribe_user(websocket, message.get("topics", []))
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
