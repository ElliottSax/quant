"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import trades, politicians, stats

api_router = APIRouter()

# Include sub-routers
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(politicians.router, prefix="/politicians", tags=["politicians"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
