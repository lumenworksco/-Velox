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
import os
from datetime import datetime
from dotenv import load_dotenv

from backend.api import trading, backtest, portfolio, market_data, strategies, settings, positions, risk, trades, system
from backend.core.websocket_manager import ConnectionManager
from core import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate required environment variables on startup"""
    warnings = []
    errors = []

    # Check Alpaca API keys
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')

    if not alpaca_key:
        warnings.append("ALPACA_API_KEY not set - trading features will be limited")
    if not alpaca_secret:
        warnings.append("ALPACA_SECRET_KEY not set - trading features will be limited")

    # Check trading mode
    paper_trading = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'
    if paper_trading:
        logger.info("🔵 Running in PAPER TRADING mode (simulated funds)")
    else:
        logger.warning("🔴 Running in LIVE TRADING mode (real money) - USE WITH CAUTION!")

    # Log warnings and errors
    for warning in warnings:
        logger.warning(f"⚠️  {warning}")

    for error in errors:
        logger.error(f"❌ {error}")

    if errors:
        raise RuntimeError("Required environment variables missing. Check logs above.")

    return {
        'alpaca_configured': bool(alpaca_key and alpaca_secret),
        'paper_trading': paper_trading,
        'warnings': warnings
    }


# Validate environment on startup
try:
    env_status = validate_environment()
    logger.info("✅ Environment validation complete")
except Exception as e:
    logger.error(f"Environment validation failed: {e}")
    # Continue anyway but with limited functionality
    env_status = {
        'alpaca_configured': False,
        'paper_trading': True,
        'warnings': ['Environment validation failed']
    }

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
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(positions.router, prefix="/api/positions", tags=["Positions"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk Management"])
app.include_router(trades.router, prefix="/api/trades", tags=["Trade History"])
app.include_router(system.router, prefix="/api/system", tags=["System Health"])


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
    """
    Health check endpoint for monitoring.
    Returns detailed system status.
    """
    try:
        # Check environment configuration
        alpaca_configured = bool(os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'))

        # Check if we're in paper trading mode
        paper_trading = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

        # Get system status
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        health_status = {
            "status": "healthy",
            "service": "alphaflow-backend",
            "version": "7.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "alpaca_configured": alpaca_configured,
                "paper_trading": paper_trading,
                "warnings": env_status.get('warnings', [])
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2)
            }
        }

        # Mark as unhealthy if critical issues
        if not alpaca_configured:
            health_status["status"] = "degraded"
            health_status["message"] = "Alpaca API not configured - trading features limited"

        if cpu_percent > 90 or memory.percent > 90:
            health_status["status"] = "degraded"
            health_status["message"] = "High resource usage"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "alphaflow-backend",
            "error": str(e)
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
