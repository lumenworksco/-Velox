"""Tax-Loss Harvesting (OPS-001).

Scans portfolio positions for unrealized losses that exceed a configurable
threshold and generates harvest actions. Enforces IRS wash sale rules
(30-day lookback/look-forward) and suggests correlated substitute
positions to maintain exposure.

Cost basis methods:
    FIFO  — First In, First Out
    LIFO  — Last In, First Out
    HIFO  — Highest In, First Out (most aggressive harvesting)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Wash sale window (calendar days, not trading days)
WASH_SALE_WINDOW_DAYS = 30

# Default loss threshold for harvesting consideration
DEFAULT_HARVEST_THRESHOLD_USD = 500

# Short-term vs long-term capital gains boundary
SHORT_TERM_HOLDING_DAYS = 365

# Correlated substitutes for maintaining sector exposure after harvest
# Maps symbol -> list of substitutes that avoid wash sale issues
SUBSTITUTE_MAP = {
    # Technology
    "AAPL": ["XLK", "QQQ", "MSFT"],
    "MSFT": ["XLK", "QQQ", "AAPL"],
    "NVDA": ["SMH", "SOXX", "AMD"],
    "AMD": ["SMH", "SOXX", "NVDA"],
    "GOOGL": ["XLC", "META", "QQQ"],
    "META": ["XLC", "GOOGL", "QQQ"],
    "TSLA": ["XLY", "ARKK", "QQQ"],
    "AMZN": ["XLY", "QQQ", "SHOP"],
    # Financials
    "JPM": ["XLF", "BAC", "GS"],
    "BAC": ["XLF", "JPM", "GS"],
    "GS": ["XLF", "JPM", "BAC"],
    # Energy
    "XOM": ["XLE", "CVX"],
    "CVX": ["XLE", "XOM"],
    # ETFs
    "SPY": ["VOO", "IVV"],
    "QQQ": ["QQQM", "XLK"],
    "IWM": ["VTWO", "SCHA"],
}


class CostBasisMethod(Enum):
    """Cost basis accounting method."""
    FIFO = "fifo"
    LIFO = "lifo"
    HIFO = "hifo"


@dataclass
class TaxLot:
    """A single tax lot (purchase) of a security."""
    symbol: str
    shares: float
    cost_basis_per_share: float
    purchase_date: date
    lot_id: str = ""

    @property
    def total_cost(self) -> float:
        return self.shares * self.cost_basis_per_share

    @property
    def holding_days(self) -> int:
        return (date.today() - self.purchase_date).days

    @property
    def is_long_term(self) -> bool:
        return self.holding_days > SHORT_TERM_HOLDING_DAYS


@dataclass
class HarvestAction:
    """A recommended tax-loss harvesting action."""
    symbol: str
    shares_to_sell: float
    estimated_loss: float
    cost_basis_per_share: float
    current_price: float
    is_short_term: bool
    tax_lots_used: List[str]           # lot_ids consumed
    substitute_symbols: List[str]      # Suggested replacements
    wash_sale_clear_date: date         # Earliest date to repurchase
    reason: str = ""


@dataclass
class SaleRecord:
    """Record of a completed sale for wash sale tracking."""
    symbol: str
    sale_date: date
    shares: float
    proceeds: float
    was_loss: bool


class TaxLossHarvester:
    """Tax-loss harvesting engine.

    Scans positions for harvestable losses, checks wash sale constraints,
    and generates harvest actions with correlated substitute suggestions.

    Usage:
        harvester = TaxLossHarvester(method=CostBasisMethod.HIFO)
        actions = harvester.scan_for_harvesting(positions, threshold=500)
        is_wash = harvester.check_wash_sale("AAPL", date.today())
    """

    def __init__(
        self,
        method: CostBasisMethod = CostBasisMethod.HIFO,
        substitute_map: Optional[Dict[str, List[str]]] = None,
    ):
        self.method = method
        self.substitute_map = substitute_map or dict(SUBSTITUTE_MAP)
        self._sale_history: List[SaleRecord] = []
        self._purchase_history: Dict[str, List[date]] = {}  # symbol -> purchase dates

    def scan_for_harvesting(
        self,
        positions: Dict[str, Dict[str, Any]],
        threshold: float = DEFAULT_HARVEST_THRESHOLD_USD,
    ) -> List[HarvestAction]:
        """Scan all positions for tax-loss harvesting opportunities.

        Args:
            positions: Dict mapping symbol -> {
                "shares": float,
                "current_price": float,
                "tax_lots": List[TaxLot],
            }
            threshold: Minimum unrealized loss (USD) to consider harvesting.

        Returns:
            List of HarvestAction recommendations, sorted by loss magnitude.
        """
        actions: List[HarvestAction] = []

        for symbol, pos_data in positions.items():
            try:
                shares = pos_data.get("shares", 0)
                current_price = pos_data.get("current_price", 0)
                tax_lots = pos_data.get("tax_lots", [])

                if shares <= 0 or current_price <= 0 or not tax_lots:
                    continue

                # Check wash sale constraint
                if self.check_wash_sale(symbol, date.today()):
                    logger.debug(
                        f"Tax harvest: skipping {symbol} — wash sale window active"
                    )
                    continue

                # Select lots based on cost basis method
                selected_lots = self._select_lots(tax_lots, current_price)

                # Calculate total harvestable loss
                total_loss = 0.0
                shares_to_sell = 0.0
                lot_ids_used = []

                for lot in selected_lots:
                    lot_loss = (current_price - lot.cost_basis_per_share) * lot.shares
                    if lot_loss < 0:  # Only harvest losses
                        total_loss += lot_loss
                        shares_to_sell += lot.shares
                        lot_ids_used.append(lot.lot_id)

                if abs(total_loss) < threshold:
                    continue

                # Determine if short-term or long-term
                # Use the first selected lot's holding period
                is_short_term = not selected_lots[0].is_long_term if selected_lots else True

                # Find substitutes
                substitutes = self._find_substitutes(symbol)

                action = HarvestAction(
                    symbol=symbol,
                    shares_to_sell=shares_to_sell,
                    estimated_loss=round(total_loss, 2),
                    cost_basis_per_share=round(
                        sum(l.cost_basis_per_share * l.shares for l in selected_lots)
                        / max(shares_to_sell, 1e-9),
                        4,
                    ),
                    current_price=round(current_price, 2),
                    is_short_term=is_short_term,
                    tax_lots_used=lot_ids_used,
                    substitute_symbols=substitutes,
                    wash_sale_clear_date=date.today() + timedelta(days=WASH_SALE_WINDOW_DAYS + 1),
                    reason=(
                        f"{'Short' if is_short_term else 'Long'}-term loss of "
                        f"${abs(total_loss):,.2f} on {shares_to_sell:.0f} shares"
                    ),
                )
                actions.append(action)

            except Exception as e:
                logger.debug(f"Tax harvest scan failed for {symbol}: {e}")
                continue

        # Sort by largest loss first (most beneficial to harvest)
        actions.sort(key=lambda a: a.estimated_loss)

        if actions:
            total_harvestable = sum(a.estimated_loss for a in actions)
            logger.info(
                f"Tax harvest scan: {len(actions)} opportunities, "
                f"total harvestable loss: ${abs(total_harvestable):,.2f}"
            )

        return actions

    def check_wash_sale(self, symbol: str, check_date: date) -> bool:
        """Check if a symbol is within the wash sale window.

        IMPL-005: Enhanced wash sale enforcement covers:
        1. Direct repurchase: same symbol bought within 30 days of loss sale
        2. Substantially identical: substitute securities bought within window
        3. Forward-looking: planned purchase would trigger wash sale on past loss

        The wash sale rule disallows claiming a loss if a "substantially
        identical" security was purchased within 30 days before or after
        the sale.

        Args:
            symbol: The ticker symbol to check.
            check_date: The date to check (typically today).

        Returns:
            True if wash sale restriction applies (do NOT sell for loss).
        """
        window_start = check_date - timedelta(days=WASH_SALE_WINDOW_DAYS)
        window_end = check_date + timedelta(days=WASH_SALE_WINDOW_DAYS)

        # Build set of "substantially identical" symbols for this security
        substantially_identical = self._get_substantially_identical(symbol)

        # Check 1: Was this symbol (or substantially identical) sold at a loss recently?
        for sale in self._sale_history:
            if not sale.was_loss:
                continue
            if sale.symbol != symbol and sale.symbol not in substantially_identical:
                continue
            if window_start <= sale.sale_date <= window_end:
                return True

        # Check 2: Was this symbol (or substantially identical) purchased recently
        # after a loss sale?
        symbols_to_check = {symbol} | substantially_identical
        for check_sym in symbols_to_check:
            purchases = self._purchase_history.get(check_sym, [])
            for purchase_date in purchases:
                if window_start <= purchase_date <= window_end:
                    # Check if there was a loss sale within window of this purchase
                    for sale in self._sale_history:
                        if sale.symbol in symbols_to_check and sale.was_loss:
                            if abs((sale.sale_date - purchase_date).days) <= WASH_SALE_WINDOW_DAYS:
                                return True

        return False

    def _get_substantially_identical(self, symbol: str) -> Set[str]:
        """Get the set of securities considered 'substantially identical' to a symbol.

        IMPL-005: IRS considers these substantially identical:
        - Same stock (obvious)
        - Options on the same stock
        - Convertible securities for the same stock
        Note: Different ETFs tracking different indices are NOT substantially identical,
        which is why we use ETF substitutes for sector exposure.
        """
        # For individual stocks, there are no substantially identical alternatives
        # in our equity-only universe. This is used defensively to catch
        # cases where the same symbol appears with different tickers (e.g., class shares).
        identical: Set[str] = set()

        # Check for share class variants
        base = symbol.rstrip("AB")
        share_classes = [f"{base}A", f"{base}B", f"{base}.A", f"{base}.B"]
        for sc in share_classes:
            if sc != symbol:
                identical.add(sc)

        # Google special case
        if symbol in ("GOOGL", "GOOG"):
            identical.add("GOOGL")
            identical.add("GOOG")
            identical.discard(symbol)

        return identical

    def record_sale(
        self, symbol: str, sale_date: date, shares: float,
        proceeds: float, cost_basis: float
    ):
        """Record a completed sale for wash sale tracking.

        Args:
            symbol: Ticker sold.
            sale_date: Date of sale.
            shares: Number of shares sold.
            proceeds: Total sale proceeds.
            cost_basis: Total cost basis of shares sold.
        """
        was_loss = proceeds < cost_basis
        self._sale_history.append(SaleRecord(
            symbol=symbol,
            sale_date=sale_date,
            shares=shares,
            proceeds=proceeds,
            was_loss=was_loss,
        ))

        # Prune old records (keep 1 year)
        cutoff = date.today() - timedelta(days=400)
        self._sale_history = [
            s for s in self._sale_history if s.sale_date > cutoff
        ]

    def record_purchase(self, symbol: str, purchase_date: date):
        """Record a purchase for wash sale tracking."""
        if symbol not in self._purchase_history:
            self._purchase_history[symbol] = []
        self._purchase_history[symbol].append(purchase_date)

        # Prune old records
        cutoff = date.today() - timedelta(days=400)
        self._purchase_history[symbol] = [
            d for d in self._purchase_history[symbol] if d > cutoff
        ]


    def _select_lots(
        self, tax_lots: List[TaxLot], current_price: float
    ) -> List[TaxLot]:
        """Select tax lots for sale based on the configured cost basis method.

        Only selects lots that are currently at a loss.
        """
        # Filter to loss lots only
        loss_lots = [
            lot for lot in tax_lots
            if lot.cost_basis_per_share > current_price and lot.shares > 0
        ]

        if not loss_lots:
            return []

        if self.method == CostBasisMethod.FIFO:
            return sorted(loss_lots, key=lambda l: l.purchase_date)
        elif self.method == CostBasisMethod.LIFO:
            return sorted(loss_lots, key=lambda l: l.purchase_date, reverse=True)
        elif self.method == CostBasisMethod.HIFO:
            return sorted(loss_lots, key=lambda l: l.cost_basis_per_share, reverse=True)
        else:
            return loss_lots

    def _find_substitutes(self, symbol: str) -> List[str]:
        """Find correlated substitute securities for maintaining exposure.

        After harvesting, the investor typically wants to maintain similar
        market exposure without triggering a wash sale. Substitutes must be
        "not substantially identical" per IRS rules.
        """
        return self.substitute_map.get(symbol, [])

