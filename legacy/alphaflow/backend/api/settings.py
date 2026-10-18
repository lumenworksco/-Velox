"""Settings API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()


class APIKeysRequest(BaseModel):
    """API keys configuration"""
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key: Optional[str] = None
    paper_trading: bool = True


class RiskSettingsRequest(BaseModel):
    """Risk management settings"""
    max_position_size: float
    max_daily_loss: float
    stop_loss_percent: float
    take_profit_percent: float


class Settings(BaseModel):
    """User settings"""
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key_set: bool = False
    paper_trading: bool = True
    max_position_size: float = 10000
    max_daily_loss: float = 5000
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 5.0
    dark_mode: bool = True


@router.get("/", response_model=Settings)
async def get_settings():
    """Get current settings"""
    try:
        # Check if .env file exists
        env_path = Path.cwd() / '.env'
        alpaca_key = os.getenv('ALPACA_API_KEY')
        alpaca_secret = os.getenv('ALPACA_SECRET_KEY')

        return Settings(
            alpaca_api_key=alpaca_key[:8] + '...' if alpaca_key else None,
            alpaca_secret_key_set=bool(alpaca_secret),
            paper_trading=os.getenv('ALPACA_PAPER', 'true').lower() == 'true',
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', '10000')),
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', '5000')),
            stop_loss_percent=float(os.getenv('STOP_LOSS_PERCENT', '2.0')),
            take_profit_percent=float(os.getenv('TAKE_PROFIT_PERCENT', '5.0')),
            dark_mode=True
        )

    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api-keys")
async def update_api_keys(keys: APIKeysRequest):
    """Update API keys"""
    try:
        env_path = Path.cwd() / '.env'

        # Read existing .env file or create new
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()

        # Update keys
        if keys.alpaca_api_key:
            env_content['ALPACA_API_KEY'] = keys.alpaca_api_key
        if keys.alpaca_secret_key:
            env_content['ALPACA_SECRET_KEY'] = keys.alpaca_secret_key
        env_content['ALPACA_PAPER'] = 'true' if keys.paper_trading else 'false'

        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')

        # Update environment variables
        if keys.alpaca_api_key:
            os.environ['ALPACA_API_KEY'] = keys.alpaca_api_key
        if keys.alpaca_secret_key:
            os.environ['ALPACA_SECRET_KEY'] = keys.alpaca_secret_key
        os.environ['ALPACA_PAPER'] = 'true' if keys.paper_trading else 'false'

        return {"success": True, "message": "API keys updated successfully"}

    except Exception as e:
        logger.error(f"Error updating API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/risk")
async def update_risk_settings(risk: RiskSettingsRequest):
    """Update risk management settings"""
    try:
        env_path = Path.cwd() / '.env'

        # Read existing .env file
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()

        # Update risk settings
        env_content['MAX_POSITION_SIZE'] = str(risk.max_position_size)
        env_content['MAX_DAILY_LOSS'] = str(risk.max_daily_loss)
        env_content['STOP_LOSS_PERCENT'] = str(risk.stop_loss_percent)
        env_content['TAKE_PROFIT_PERCENT'] = str(risk.take_profit_percent)

        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')

        # Update environment variables
        os.environ['MAX_POSITION_SIZE'] = str(risk.max_position_size)
        os.environ['MAX_DAILY_LOSS'] = str(risk.max_daily_loss)
        os.environ['STOP_LOSS_PERCENT'] = str(risk.stop_loss_percent)
        os.environ['TAKE_PROFIT_PERCENT'] = str(risk.take_profit_percent)

        return {"success": True, "message": "Risk settings updated successfully"}

    except Exception as e:
        logger.error(f"Error updating risk settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trading-mode")
async def get_trading_mode():
    """Get current trading mode (paper or live)"""
    mode = "paper" if os.getenv('ALPACA_PAPER', 'true').lower() == 'true' else "live"
    return {"mode": mode}


@router.put("/trading-mode")
async def set_trading_mode(mode: str):
    """
    Set trading mode (paper or live)

    WARNING: Live trading uses real money!
    """
    if mode not in ["paper", "live"]:
        raise HTTPException(status_code=400, detail="Mode must be 'paper' or 'live'")

    try:
        env_path = Path.cwd() / '.env'

        # Read existing .env file
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()

        # Update mode
        env_content['ALPACA_PAPER'] = 'true' if mode == 'paper' else 'false'

        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')

        # Update environment variable
        os.environ['ALPACA_PAPER'] = 'true' if mode == 'paper' else 'false'

        # Get previous mode for notification
        previous_mode = "paper" if os.getenv('ALPACA_PAPER', 'true').lower() == 'true' else "live"

        if mode == "live":
            logger.warning("🔴 TRADING MODE SET TO LIVE - REAL MONEY AT RISK")
        else:
            logger.info("🔵 Trading mode set to PAPER (simulated)")

        # Send notification
        from backend.notification_system import notification_system
        notification_system.alert_trading_mode_changed(
            old_mode=previous_mode,
            new_mode=mode
        )

        return {
            "success": True,
            "mode": mode,
            "message": f"Trading mode set to {mode.upper()}"
        }

    except Exception as e:
        logger.error(f"Error setting trading mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))
