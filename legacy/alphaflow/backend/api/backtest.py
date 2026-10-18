"""Backtest API endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date
import logging
import uuid

from core import BacktestEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Store running backtests
active_backtests: Dict[str, dict] = {}


class BacktestRequest(BaseModel):
    """Backtest configuration"""
    symbols: List[str]
    strategy: str
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    commission: float = 0.001


class BacktestStatus(BaseModel):
    """Backtest execution status"""
    backtest_id: str
    status: str  # 'running', 'completed', 'failed'
    progress: int  # 0-100
    message: str


class BacktestResult(BaseModel):
    """Backtest results"""
    backtest_id: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    final_equity: float
    execution_time: float


@router.post("/run", response_model=BacktestStatus)
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """
    Start a new backtest execution.

    Returns backtest ID for status polling.
    """
    try:
        # Generate unique backtest ID
        backtest_id = str(uuid.uuid4())

        # Initialize backtest
        active_backtests[backtest_id] = {
            "status": "running",
            "progress": 0,
            "message": "Initializing backtest...",
            "config": request.dict()
        }

        # Run backtest in background
        background_tasks.add_task(execute_backtest, backtest_id, request)

        return BacktestStatus(
            backtest_id=backtest_id,
            status="running",
            progress=0,
            message="Backtest started"
        )

    except Exception as e:
        logger.error(f"Error starting backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{backtest_id}", response_model=BacktestStatus)
async def get_backtest_status(backtest_id: str):
    """Get status of a running or completed backtest"""
    if backtest_id not in active_backtests:
        raise HTTPException(status_code=404, detail="Backtest not found")

    info = active_backtests[backtest_id]

    return BacktestStatus(
        backtest_id=backtest_id,
        status=info['status'],
        progress=info['progress'],
        message=info['message']
    )


@router.get("/results/{backtest_id}", response_model=BacktestResult)
async def get_backtest_results(backtest_id: str):
    """Get results of a completed backtest"""
    if backtest_id not in active_backtests:
        raise HTTPException(status_code=404, detail="Backtest not found")

    info = active_backtests[backtest_id]

    if info['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Backtest not yet completed")

    results = info.get('results', {})

    return BacktestResult(
        backtest_id=backtest_id,
        total_return=results.get('total_return', 0.0),
        sharpe_ratio=results.get('sharpe_ratio', 0.0),
        max_drawdown=results.get('max_drawdown', 0.0),
        win_rate=results.get('win_rate', 0.0),
        total_trades=results.get('total_trades', 0),
        final_equity=results.get('final_equity', 0.0),
        execution_time=results.get('execution_time', 0.0)
    )


@router.delete("/{backtest_id}")
async def cancel_backtest(backtest_id: str):
    """Cancel a running backtest"""
    if backtest_id not in active_backtests:
        raise HTTPException(status_code=404, detail="Backtest not found")

    active_backtests[backtest_id]['status'] = 'canceled'
    active_backtests[backtest_id]['message'] = 'Backtest canceled by user'

    return {"success": True, "message": "Backtest canceled"}


async def execute_backtest(backtest_id: str, request: BacktestRequest):
    """Execute backtest in background"""
    import time
    start_time = time.time()

    try:
        # Update progress
        active_backtests[backtest_id]['progress'] = 10
        active_backtests[backtest_id]['message'] = "Fetching historical data..."

        # Create backtest engine
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission=request.commission
        )

        active_backtests[backtest_id]['progress'] = 30
        active_backtests[backtest_id]['message'] = "Running strategy..."

        # Run backtest
        raw_results = engine.run_backtest(
            symbols=request.symbols,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            strategy=request.strategy
        )

        # Extract overall results and format for API response
        if raw_results.get('success'):
            overall = raw_results.get('overall_results', {})

            # Check if we actually got valid data
            if not overall or overall.get('symbols_tested', 0) == 0:
                # No valid symbols found
                active_backtests[backtest_id]['status'] = 'failed'
                active_backtests[backtest_id]['message'] = f"No valid data found for symbols: {', '.join(request.symbols)}. Please check symbol names."
                active_backtests[backtest_id]['progress'] = 0
                return

            execution_time = time.time() - start_time

            # Format results for API
            results = {
                'total_return': overall.get('total_return', 0.0) / 100,  # Convert to decimal
                'sharpe_ratio': overall.get('avg_sharpe_ratio', 0.0),
                'max_drawdown': overall.get('max_drawdown', 0.0) / 100,  # Convert to decimal
                'win_rate': overall.get('avg_win_rate', 0.0) / 100,  # Convert to decimal
                'total_trades': overall.get('total_trades', 0),
                'final_equity': overall.get('final_capital', request.initial_capital),
                'execution_time': execution_time
            }
        else:
            # Backtest failed - check the error message
            error_msg = raw_results.get('error', 'Unknown error')
            active_backtests[backtest_id]['status'] = 'failed'
            active_backtests[backtest_id]['message'] = error_msg
            active_backtests[backtest_id]['progress'] = 0
            return

        # Store results
        active_backtests[backtest_id]['progress'] = 100
        active_backtests[backtest_id]['status'] = 'completed'
        active_backtests[backtest_id]['message'] = 'Backtest completed'
        active_backtests[backtest_id]['results'] = results

        logger.info(f"Backtest {backtest_id} completed successfully")

    except Exception as e:
        logger.error(f"Backtest {backtest_id} failed: {e}", exc_info=True)
        active_backtests[backtest_id]['status'] = 'failed'
        active_backtests[backtest_id]['message'] = f"Backtest error: {str(e)}"
        active_backtests[backtest_id]['progress'] = 0
