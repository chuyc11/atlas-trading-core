"""v1.2.0 A-share local autonomous ops scheduling and continuous simulation."""

from trading_core.equity_v12_continuous_ops.audit import audit_a_share_v12_continuous_ops
from trading_core.equity_v12_continuous_ops.builder import DEFAULT_AS_OF_DATE, run_a_share_v12_continuous_ops

__all__ = ["DEFAULT_AS_OF_DATE", "audit_a_share_v12_continuous_ops", "run_a_share_v12_continuous_ops"]
