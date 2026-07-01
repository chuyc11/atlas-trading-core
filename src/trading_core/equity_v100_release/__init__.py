"""Official v1.0.0 release closeout for the A-share simulation platform."""

from trading_core.equity_v100_release.audit import audit_a_share_v100_release
from trading_core.equity_v100_release.builder import DEFAULT_AS_OF_DATE, build_a_share_v100_release

__all__ = ["DEFAULT_AS_OF_DATE", "audit_a_share_v100_release", "build_a_share_v100_release"]
