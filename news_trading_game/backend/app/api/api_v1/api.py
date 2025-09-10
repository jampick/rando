from fastapi import APIRouter
from app.api.api_v1.endpoints import markets, trading, portfolio, users

api_router = APIRouter()

api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
