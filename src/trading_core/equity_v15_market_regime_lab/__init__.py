"""v1.5.0 A-share market regime and adaptive research simulation."""

from trading_core.equity_v15_market_regime_lab.audit import audit_a_share_v15_market_regime_lab
from trading_core.equity_v15_market_regime_lab.builder import DEFAULT_AS_OF_DATE, run_a_share_v15_market_regime_lab

__all__ = [
    "DEFAULT_AS_OF_DATE",
    "audit_a_share_v15_market_regime_lab",
    "run_a_share_v15_market_regime_lab",
]
