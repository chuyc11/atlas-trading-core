"""A-share benchmark comparison package."""

from trading_core.equity_benchmarks.benchmark_audit import audit_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_builder import build_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_config import TARGET_VERSION

__all__ = ["TARGET_VERSION", "audit_a_share_benchmark_comparison", "build_a_share_benchmark_comparison"]
