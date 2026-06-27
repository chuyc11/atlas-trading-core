"""Configuration for the A-share tradable universe filter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TARGET_VERSION = "v0.7.2-a-share-tradable-universe-filter"
RECOMMENDED_NEXT_VERSION = "v0.7.3-a-share-multi-horizon-feature-engineering"
REMEDIATION_VERSION = "v0.7.2.1-a-share-tradable-universe-filter-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

TRADABLE_UNIVERSE_BOUNDARY = {
    "tradable_universe_filter_only": True,
    "scores_generated": False,
    "candidates_generated": False,
    "watchlist_generated": False,
    "virtual_portfolio_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}


@dataclass(frozen=True)
class TradableUniverseFilterConfig:
    """Thresholds and execution flags for v0.7.2 tradable universe filtering."""

    as_of_date: str = DEFAULT_AS_OF_DATE
    min_listing_trading_days: int = 120
    min_effective_trading_days_20d: int = 18
    min_effective_trading_days_60d: int = 50
    min_avg_amount_20d: float = 50_000_000
    min_avg_amount_60d: float = 30_000_000
    min_total_mv: float = 3_000_000_000
    min_circ_mv: float = 2_000_000_000
    min_close_price: float = 2.0
    require_20d_history: bool = True
    require_60d_history: bool = True
    require_120d_history: bool = True
    require_250d_history: bool = True
    include_caution: bool = False
    allow_previous_trading_day: bool = False

    def thresholds(self) -> dict[str, Any]:
        return {
            "min_listing_trading_days": self.min_listing_trading_days,
            "min_effective_trading_days_20d": self.min_effective_trading_days_20d,
            "min_effective_trading_days_60d": self.min_effective_trading_days_60d,
            "min_avg_amount_20d": self.min_avg_amount_20d,
            "min_avg_amount_60d": self.min_avg_amount_60d,
            "min_total_mv": self.min_total_mv,
            "min_circ_mv": self.min_circ_mv,
            "min_close_price": self.min_close_price,
            "require_20d_history": self.require_20d_history,
            "require_60d_history": self.require_60d_history,
            "require_120d_history": self.require_120d_history,
            "require_250d_history": self.require_250d_history,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "target_version": TARGET_VERSION,
            "thresholds": self.thresholds(),
            "boundary": dict(TRADABLE_UNIVERSE_BOUNDARY),
        }


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")

