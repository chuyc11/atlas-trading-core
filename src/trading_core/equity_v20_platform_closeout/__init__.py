"""A-share v2.0.0 research-only simulation platform closeout."""

from trading_core.equity_v20_platform_closeout.audit import audit_a_share_v20_platform_closeout
from trading_core.equity_v20_platform_closeout.builder import DEFAULT_AS_OF_DATE, run_a_share_v20_platform_closeout

__all__ = ["DEFAULT_AS_OF_DATE", "audit_a_share_v20_platform_closeout", "run_a_share_v20_platform_closeout"]
