"""v1.0.1 A-share benchmark data and performance claim hardening."""

from trading_core.equity_benchmark_claim_hardening.audit import audit_a_share_benchmark_claim_hardening
from trading_core.equity_benchmark_claim_hardening.builder import DEFAULT_AS_OF_DATE, build_a_share_benchmark_claim_hardening

__all__ = ["DEFAULT_AS_OF_DATE", "audit_a_share_benchmark_claim_hardening", "build_a_share_benchmark_claim_hardening"]
