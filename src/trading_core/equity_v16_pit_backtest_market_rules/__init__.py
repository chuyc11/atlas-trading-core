"""v1.6.0 A-share point-in-time backtest and market rule hardening."""

from trading_core.equity_v16_pit_backtest_market_rules.audit import audit_a_share_v16_pit_backtest_market_rules
from trading_core.equity_v16_pit_backtest_market_rules.builder import DEFAULT_AS_OF_DATE, run_a_share_v16_pit_backtest_market_rules

__all__ = [
    "DEFAULT_AS_OF_DATE",
    "audit_a_share_v16_pit_backtest_market_rules",
    "run_a_share_v16_pit_backtest_market_rules",
]
