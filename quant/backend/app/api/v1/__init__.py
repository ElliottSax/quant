"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import auth, patterns, politicians, stats, tasks, trades

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(politicians.router, prefix="/politicians", tags=["politicians"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
api_router.include_router(tasks.router, tags=["tasks"])
