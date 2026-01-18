"""
AlphaFlow FastAPI Backend - Main Application
Professional algorithmic trading platform API
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List
import asyncio

from backend.api import trading, backtest, portfolio, market_data, strategies
from backend.core.websocket_manager import ConnectionManager
from core import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AlphaFlow Trading API",
    description="Professional algorithmic trading platform backend",
    version="7.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include API routers
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(market_data.router, prefix="/api/market", tags=["Market Data"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])


@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "name": "AlphaFlow Trading API",
        "version": "7.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "alphaflow-backend"
    }


@app.websocket("/ws/market-data")
async def websocket_market_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data streaming.

    Sends live price updates for symbols in user's watchlist.
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive watchlist symbols from client
            data = await websocket.receive_json()
            symbols = data.get("symbols", [])

            # Stream market data for these symbols
            # This would integrate with Alpaca WebSocket API
            await manager.broadcast({
                "type": "market_update",
                "data": {
                    "symbol": "AAPL",
                    "price": 185.25,
                    "change": 2.50,
                    "change_percent": 1.37
                }
            })

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("AlphaFlow API starting up...")
    # Initialize trading engine, data sources, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("AlphaFlow API shutting down...")
    # Close connections, save state, etc.


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
