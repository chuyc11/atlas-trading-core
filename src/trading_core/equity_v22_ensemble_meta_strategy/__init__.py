"""A-share v2.2.0 ensemble and meta-strategy research-only expansion."""

from trading_core.equity_v22_ensemble_meta_strategy.audit import audit_a_share_v22_ensemble_meta_strategy
from trading_core.equity_v22_ensemble_meta_strategy.builder import DEFAULT_AS_OF_DATE, run_a_share_v22_ensemble_meta_strategy

__all__ = ["DEFAULT_AS_OF_DATE", "audit_a_share_v22_ensemble_meta_strategy", "run_a_share_v22_ensemble_meta_strategy"]
