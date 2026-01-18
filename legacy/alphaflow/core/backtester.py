"""Backtesting engine for Version 6 Trading App."""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .config import TradingConfig
from .data_fetcher import SimplifiedDataFetcher
from .indicators import AdvancedIndicators
from .ml_predictor import MLPredictor
from .strategies import TradingStrategies
from .data_structures import SignalAction


class BacktestEngine:
    """Comprehensive backtesting engine for Version 6."""

    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.data_fetcher = SimplifiedDataFetcher()
        self.ml_predictor = MLPredictor()
        self.strategies = TradingStrategies(self.ml_predictor)
    
    def run_backtest(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        strategy: str = "Technical Momentum",
        commission: Optional[float] = None
    ) -> Dict:
        """Run comprehensive backtest on multiple symbols."""

        # Use provided commission or fall back to instance commission
        comm = commission if commission is not None else self.commission

        self.logger.info(f"Starting backtest for symbols: {symbols} with commission: {comm}")

        # Determine data period
        period = self._determine_period(start_date, end_date)
        
        # Fetch data for all symbols
        data_dict = self.data_fetcher.fetch_data_parallel(symbols, period=period)
        
        # Filter out symbols with insufficient data
        valid_data = {
            symbol: data for symbol, data in data_dict.items() 
            if data is not None and len(data) >= 50
        }
        
        if not valid_data:
            self.logger.error("No valid data for backtesting")
            return {
                'success': False,
                'error': 'No valid data for backtesting',
                'overall_results': {},
                'symbol_results': {},
                'equity_curve': [],
                'trades': []
            }
        
        self.logger.info(f"Backtesting {len(valid_data)} symbols with sufficient data")
        
        # Run backtest for each symbol
        symbol_results = {}
        all_trades = []
        all_equity = []
        
        capital_per_symbol = self.initial_capital / len(valid_data)
        
        for symbol, data in valid_data.items():
            self.logger.info(f"Backtesting {symbol}...")
            
            result, trades, equity = self._backtest_symbol(
                symbol, data, capital_per_symbol, strategy, commission
            )
            symbol_results[symbol] = result
            all_trades.extend(trades)
            
            # Add symbol to equity data
            for eq in equity:
                eq['symbol'] = symbol
            all_equity.extend(equity)
        
        # Calculate overall results
        overall_results = self._calculate_overall_results(symbol_results, all_trades)
        
        return {
            'success': True,
            'overall_results': overall_results,
            'symbol_results': symbol_results,
            'trades': all_trades,
            'equity_curve': all_equity,
            'symbols_tested': list(valid_data.keys())
        }
    
    def _determine_period(self, start_date: str = None, end_date: str = None) -> str:
        """Determine appropriate data period."""
        if start_date:
            try:
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date) if end_date else datetime.now()
                period_days = (end - start).days
                
                if period_days > 365:
                    return "2y"
                elif period_days > 180:
                    return "1y"
                elif period_days > 90:
                    return "6mo"
                else:
                    return "3mo"
            except Exception:
                return "1y"
        else:
            return "1y"
    
    def _backtest_symbol(
        self,
        symbol: str,
        data: pd.DataFrame,
        initial_capital: float,
        strategy: str,
        commission: float
    ) -> Tuple[Dict, List[Dict], List[Dict]]:
        """Backtest a single symbol."""
        
        # Calculate technical indicators
        data_with_indicators = AdvancedIndicators.calculate_all_indicators(data)
        
        # Train ML model on first portion of data
        train_size = min(100, len(data_with_indicators) // 3)
        if train_size >= 50:
            train_data = data_with_indicators.iloc[:train_size]
            self.ml_predictor.train(train_data)
        
        # Initialize backtest state
        capital = initial_capital
        position = None  # Single position per symbol
        trades = []
        equity_curve = []
        
        # Walk through data day by day
        lookback = 50  # Need at least 50 days for indicators
        
        for i in range(lookback, len(data_with_indicators)):
            current_date = data_with_indicators.index[i]
            current_data = data_with_indicators.iloc[:i+1]
            current_row = current_data.iloc[-1]
            current_price = current_row['close']
            
            # Record equity
            position_value = 0
            if position:
                position_value = position['quantity'] * current_price
            
            total_equity = capital + position_value
            equity_curve.append({
                'date': current_date,
                'equity': total_equity,
                'cash': capital,
                'positions_value': position_value
            })
            
            # Generate trading signals using selected strategy
            signals = self._get_strategy_signals(current_data, symbol, strategy)
            
            if signals:
                best_signal = max(signals, key=lambda x: x.confidence)
                
                # Execute buy signals
                if (best_signal.action in [SignalAction.BUY, SignalAction.STRONG_BUY]
                    and position is None 
                    and best_signal.confidence >= TradingConfig.MIN_CONFIDENCE):
                    
                    # Calculate position size (use 95% of capital)
                    max_position_value = capital * 0.95
                    position_size = int(max_position_value / current_price)
                    
                    if position_size > 0:
                        cost = position_size * current_price + commission
                        
                        if cost <= capital:
                            position = {
                                'symbol': symbol,
                                'quantity': position_size,
                                'entry_price': current_price,
                                'entry_date': current_date,
                                'stop_loss': best_signal.stop_loss,
                                'take_profit': best_signal.take_profit,
                                'strategy': best_signal.strategy
                            }
                            capital -= cost
                
                # Execute sell signals
                elif (best_signal.action in [SignalAction.SELL, SignalAction.STRONG_SELL]
                      and position is not None):
                    
                    exit_price = current_price
                    proceeds = position['quantity'] * exit_price - commission
                    pnl = proceeds - (position['quantity'] * position['entry_price'])
                    capital += proceeds
                    
                    trade = self._create_trade_record(
                        position, exit_price, pnl, current_date, "signal_exit"
                    )
                    trades.append(trade)
                    position = None
            
            # Check stop losses and take profits
            if position:
                exit_triggered = False
                exit_reason = ""
                exit_price = current_price
                
                if position.get('stop_loss') and current_price <= position['stop_loss']:
                    exit_triggered = True
                    exit_reason = "stop_loss"
                    exit_price = position['stop_loss']
                    
                elif position.get('take_profit') and current_price >= position['take_profit']:
                    exit_triggered = True
                    exit_reason = "take_profit"
                    exit_price = position['take_profit']
                
                if exit_triggered:
                    proceeds = position['quantity'] * exit_price - commission
                    pnl = proceeds - (position['quantity'] * position['entry_price'])
                    capital += proceeds
                    
                    trade = self._create_trade_record(
                        position, exit_price, pnl, current_date, exit_reason
                    )
                    trades.append(trade)
                    position = None
        
        # Close remaining position at final price
        if position:
            final_price = data_with_indicators.iloc[-1]['close']
            final_date = data_with_indicators.index[-1]
            
            proceeds = position['quantity'] * final_price - commission
            pnl = proceeds - (position['quantity'] * position['entry_price'])
            capital += proceeds
            
            trade = self._create_trade_record(
                position, final_price, pnl, final_date, "end_of_backtest"
            )
            trades.append(trade)
        
        # Calculate symbol results
        symbol_result = self._calculate_symbol_results(
            symbol, initial_capital, capital, trades, equity_curve
        )
        
        return symbol_result, trades, equity_curve
    
    def _get_strategy_signals(self, data: pd.DataFrame, symbol: str, strategy: str) -> List:
        """Get signals based on selected strategy."""
        
        if strategy == "Technical Momentum":
            signal = self.strategies.technical_momentum_strategy(data, symbol)
            return [signal] if signal else []
        
        elif strategy == "Mean Reversion":
            signal = self.strategies.mean_reversion_strategy(data, symbol)
            return [signal] if signal else []
        
        elif strategy == "Trend Following":
            signal = self.strategies.trend_following_strategy(data, symbol)
            return [signal] if signal else []
        
        elif strategy == "ML Hybrid":
            return self.strategies.generate_all_signals(data, symbol)
        
        else:
            # Use all strategies
            return self.strategies.generate_all_signals(data, symbol)
    
    def _create_trade_record(
        self,
        position: Dict,
        exit_price: float,
        pnl: float,
        exit_date,
        exit_reason: str
    ) -> Dict:
        """Create a trade record dictionary."""
        entry_value = position['quantity'] * position['entry_price']
        return {
            'symbol': position['symbol'],
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'pnl': pnl,
            'return_pct': (pnl / entry_value) * 100 if entry_value > 0 else 0,
            'strategy': position['strategy'],
            'exit_reason': exit_reason,
            'days_held': (exit_date - position['entry_date']).days
        }
    
    def _calculate_symbol_results(
        self,
        symbol: str,
        initial_capital: float,
        final_capital: float,
        trades: List[Dict],
        equity_curve: List[Dict]
    ) -> Dict:
        """Calculate results for a single symbol."""
        
        if not trades:
            return {
                'symbol': symbol,
                'total_trades': 0,
                'initial_capital': initial_capital,
                'final_capital': final_capital,
                'total_return': 0,
                'win_rate': 0,
                'avg_return_per_trade': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'profit_factor': 0
            }
        
        trades_df = pd.DataFrame(trades)
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        avg_return_per_trade = trades_df['return_pct'].mean()
        best_trade = trades_df['return_pct'].max()
        worst_trade = trades_df['return_pct'].min()
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Calculate drawdown from equity curve
        max_drawdown = 0
        sharpe_ratio = 0
        
        if equity_curve:
            equity_df = pd.DataFrame(equity_curve)
            equity_series = equity_df['equity']
            
            # Max drawdown
            peak = equity_series.expanding().max()
            drawdown = (equity_series - peak) / peak
            max_drawdown = abs(drawdown.min()) * 100
            
            # Sharpe ratio (annualized)
            equity_returns = equity_series.pct_change().dropna()
            if len(equity_returns) > 0 and equity_returns.std() > 0:
                sharpe_ratio = (equity_returns.mean() / equity_returns.std()) * np.sqrt(252)
        
        return {
            'symbol': symbol,
            'total_trades': total_trades,
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'win_rate': win_rate * 100,
            'avg_return_per_trade': avg_return_per_trade,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor,
            'avg_days_held': trades_df['days_held'].mean() if len(trades_df) > 0 else 0
        }
    
    def _calculate_overall_results(
        self,
        symbol_results: Dict,
        all_trades: List[Dict]
    ) -> Dict:
        """Calculate overall backtest results."""
        
        if not symbol_results:
            return {}
        
        # Aggregate results
        total_final_capital = sum(r['final_capital'] for r in symbol_results.values())
        total_trades = sum(r['total_trades'] for r in symbol_results.values())
        
        # Calculate averages
        returns = [r['total_return'] for r in symbol_results.values()]
        win_rates = [r['win_rate'] for r in symbol_results.values() if r['total_trades'] > 0]
        sharpe_ratios = [r['sharpe_ratio'] for r in symbol_results.values() if r['sharpe_ratio'] != 0]
        drawdowns = [r['max_drawdown'] for r in symbol_results.values()]
        
        avg_return = np.mean(returns) if returns else 0
        avg_win_rate = np.mean(win_rates) if win_rates else 0
        avg_sharpe = np.mean(sharpe_ratios) if sharpe_ratios else 0
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        overall_return = ((total_final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate profit factor from all trades
        profit_factor = 0
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            winning = trades_df[trades_df['pnl'] > 0]
            losing = trades_df[trades_df['pnl'] < 0]
            
            gross_profit = winning['pnl'].sum() if len(winning) > 0 else 0
            gross_loss = abs(losing['pnl'].sum()) if len(losing) > 0 else 1
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': total_final_capital,
            'total_return': overall_return,
            'total_trades': total_trades,
            'symbols_tested': len(symbol_results),
            'avg_return_per_symbol': avg_return,
            'avg_win_rate': avg_win_rate,
            'avg_sharpe_ratio': avg_sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor
        }
