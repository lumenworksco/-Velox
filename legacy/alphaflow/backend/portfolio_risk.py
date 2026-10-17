"""Portfolio-level risk management with heat and correlation limits"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PortfolioRiskManager:
    """Advanced portfolio risk management"""

    def __init__(
        self,
        max_portfolio_heat: float = 0.25,  # Max 25% of portfolio at risk
        max_correlated_exposure: float = 0.15,  # Max 15% in highly correlated assets
        correlation_threshold: float = 0.7  # Assets with >0.7 correlation
    ):
        """
        Initialize portfolio risk manager

        Args:
            max_portfolio_heat: Maximum portfolio heat (% at risk)
            max_correlated_exposure: Maximum exposure to correlated assets
            correlation_threshold: Correlation threshold for grouping
        """
        self.max_portfolio_heat = max_portfolio_heat
        self.max_correlated_exposure = max_correlated_exposure
        self.correlation_threshold = correlation_threshold

        # Cache for correlation calculations
        self.correlation_matrix: Optional[pd.DataFrame] = None
        self.last_correlation_update: Optional[datetime] = None
        self.correlation_cache_duration = timedelta(hours=1)  # Refresh hourly

    def calculate_portfolio_heat(
        self,
        positions: List[Dict],
        portfolio_value: float
    ) -> float:
        """
        Calculate portfolio heat (total amount at risk)

        Portfolio heat = Sum of (position size × distance to stop-loss)

        Args:
            positions: List of open positions with stop-loss levels
            portfolio_value: Total portfolio value

        Returns:
            Portfolio heat as decimal (0.15 = 15% at risk)
        """
        total_risk = 0.0

        for position in positions:
            # Skip positions without stop-loss
            if not position.get('stop_loss'):
                continue

            current_price = position.get('current_price', position.get('entry_price'))
            stop_loss = position['stop_loss']
            shares = position['shares']

            # Calculate risk per position (amount lost if stop hits)
            risk_per_share = abs(current_price - stop_loss)
            position_risk = risk_per_share * shares

            total_risk += position_risk

        # Calculate heat as percentage of portfolio
        portfolio_heat = total_risk / portfolio_value if portfolio_value > 0 else 0.0

        return portfolio_heat

    def check_portfolio_heat_limit(
        self,
        positions: List[Dict],
        portfolio_value: float
    ) -> Tuple[bool, float, str]:
        """
        Check if portfolio heat is within acceptable limits

        Args:
            positions: List of open positions
            portfolio_value: Total portfolio value

        Returns:
            (is_within_limit, current_heat, message)
        """
        current_heat = self.calculate_portfolio_heat(positions, portfolio_value)

        is_within_limit = current_heat <= self.max_portfolio_heat

        message = f"Portfolio heat: {current_heat*100:.2f}% (Limit: {self.max_portfolio_heat*100:.2f}%)"

        if not is_within_limit:
            message += " ⚠️ EXCEEDED"

        return is_within_limit, current_heat, message

    def calculate_correlation_matrix(
        self,
        symbols: List[str],
        lookback_days: int = 60
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for symbols

        Args:
            symbols: List of stock symbols
            lookback_days: Days of historical data for correlation

        Returns:
            Correlation matrix as DataFrame
        """
        try:
            # Check if we can use cached correlation
            if (self.correlation_matrix is not None and
                self.last_correlation_update is not None and
                datetime.now() - self.last_correlation_update < self.correlation_cache_duration):
                return self.correlation_matrix

            # Fetch historical data for all symbols
            import yfinance as yf
            from datetime import timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            # Download data
            logger.info(f"Calculating correlation matrix for {len(symbols)} symbols")
            data = yf.download(
                symbols,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )

            # Extract closing prices
            if len(symbols) == 1:
                closes = pd.DataFrame(data['Close'], columns=symbols)
            else:
                closes = data['Close']

            # Calculate returns
            returns = closes.pct_change().dropna()

            # Calculate correlation matrix
            corr_matrix = returns.corr()

            # Cache result
            self.correlation_matrix = corr_matrix
            self.last_correlation_update = datetime.now()

            logger.info("Correlation matrix calculated successfully")
            return corr_matrix

        except Exception as e:
            logger.error(f"Failed to calculate correlation matrix: {e}")
            # Return identity matrix as fallback (no correlation)
            return pd.DataFrame(np.eye(len(symbols)), index=symbols, columns=symbols)

    def find_correlated_clusters(
        self,
        symbols: List[str]
    ) -> List[List[str]]:
        """
        Group highly correlated assets into clusters

        Args:
            symbols: List of stock symbols

        Returns:
            List of clusters (each cluster is a list of correlated symbols)
        """
        if len(symbols) <= 1:
            return [symbols]

        # Get correlation matrix
        corr_matrix = self.calculate_correlation_matrix(symbols)

        # Find clusters using simple threshold-based grouping
        clusters = []
        assigned = set()

        for symbol in symbols:
            if symbol in assigned:
                continue

            # Find all symbols highly correlated with this one
            cluster = [symbol]
            assigned.add(symbol)

            for other_symbol in symbols:
                if other_symbol == symbol or other_symbol in assigned:
                    continue

                # Check correlation
                try:
                    correlation = corr_matrix.loc[symbol, other_symbol]
                    if correlation >= self.correlation_threshold:
                        cluster.append(other_symbol)
                        assigned.add(other_symbol)
                except KeyError:
                    continue

            clusters.append(cluster)

        logger.info(f"Found {len(clusters)} correlation clusters: {clusters}")
        return clusters

    def check_correlated_exposure(
        self,
        positions: List[Dict],
        portfolio_value: float
    ) -> Tuple[bool, float, str]:
        """
        Check if exposure to correlated assets exceeds limits

        Args:
            positions: List of open positions
            portfolio_value: Total portfolio value

        Returns:
            (is_within_limit, max_cluster_exposure, message)
        """
        if not positions:
            return True, 0.0, "No positions"

        # Get all symbols
        symbols = [p['symbol'] for p in positions]

        # Find correlated clusters
        clusters = self.find_correlated_clusters(symbols)

        # Calculate exposure per cluster
        max_cluster_exposure = 0.0
        violating_cluster = None

        for cluster in clusters:
            cluster_value = sum(
                p['shares'] * p.get('current_price', p.get('entry_price'))
                for p in positions
                if p['symbol'] in cluster
            )
            cluster_exposure = cluster_value / portfolio_value if portfolio_value > 0 else 0.0

            if cluster_exposure > max_cluster_exposure:
                max_cluster_exposure = cluster_exposure
                violating_cluster = cluster

        is_within_limit = max_cluster_exposure <= self.max_correlated_exposure

        if violating_cluster and len(violating_cluster) > 1:
            message = f"Correlated exposure ({', '.join(violating_cluster)}): {max_cluster_exposure*100:.2f}% (Limit: {self.max_correlated_exposure*100:.2f}%)"
        else:
            message = f"Max cluster exposure: {max_cluster_exposure*100:.2f}%"

        if not is_within_limit:
            message += " ⚠️ EXCEEDED"

        return is_within_limit, max_cluster_exposure, message

    def can_open_new_position(
        self,
        symbol: str,
        position_value: float,
        stop_loss_price: float,
        entry_price: float,
        existing_positions: List[Dict],
        portfolio_value: float
    ) -> Tuple[bool, str]:
        """
        Check if opening a new position would violate risk limits

        Args:
            symbol: Symbol to trade
            position_value: Value of new position
            stop_loss_price: Stop-loss price for new position
            entry_price: Entry price
            existing_positions: Currently open positions
            portfolio_value: Total portfolio value

        Returns:
            (can_open, reason)
        """
        # Create hypothetical new position
        new_position = {
            'symbol': symbol,
            'shares': position_value / entry_price,
            'entry_price': entry_price,
            'current_price': entry_price,
            'stop_loss': stop_loss_price
        }

        # Check portfolio heat with new position
        all_positions = existing_positions + [new_position]
        heat_ok, new_heat, heat_msg = self.check_portfolio_heat_limit(all_positions, portfolio_value)

        if not heat_ok:
            return False, f"Portfolio heat would exceed limit: {heat_msg}"

        # Check correlated exposure
        corr_ok, new_corr, corr_msg = self.check_correlated_exposure(all_positions, portfolio_value)

        if not corr_ok:
            return False, f"Correlated exposure would exceed limit: {corr_msg}"

        return True, f"Position approved (Heat: {new_heat*100:.1f}%, Corr: {new_corr*100:.1f}%)"

    def get_risk_report(
        self,
        positions: List[Dict],
        portfolio_value: float
    ) -> Dict:
        """
        Generate comprehensive risk report

        Args:
            positions: List of open positions
            portfolio_value: Total portfolio value

        Returns:
            Risk metrics dictionary
        """
        # Calculate metrics
        heat_ok, heat, heat_msg = self.check_portfolio_heat_limit(positions, portfolio_value)
        corr_ok, corr, corr_msg = self.check_correlated_exposure(positions, portfolio_value)

        # Find clusters
        symbols = [p['symbol'] for p in positions] if positions else []
        clusters = self.find_correlated_clusters(symbols) if symbols else []

        return {
            "portfolio_heat": {
                "current": heat,
                "limit": self.max_portfolio_heat,
                "within_limit": heat_ok,
                "message": heat_msg
            },
            "correlated_exposure": {
                "current": corr,
                "limit": self.max_correlated_exposure,
                "within_limit": corr_ok,
                "message": corr_msg
            },
            "correlation_clusters": clusters,
            "num_positions": len(positions),
            "overall_risk_ok": heat_ok and corr_ok
        }


# Global portfolio risk manager instance
portfolio_risk_manager = PortfolioRiskManager()
