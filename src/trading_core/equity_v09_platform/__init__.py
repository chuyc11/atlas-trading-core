"""A-share v0.9 autonomous research and simulation platform completion."""

from trading_core.equity_v09_platform.audit import audit_a_share_v09_platform
from trading_core.equity_v09_platform.builder import (
    DEFAULT_AS_OF_DATE,
    build_a_share_experiment_registry,
    evaluate_a_share_simulated_strategy_promotion,
    run_a_share_automated_experiments,
    run_a_share_rl_simulated_strategy_lab,
    run_a_share_v09_daily_platform,
)

__all__ = [
    "DEFAULT_AS_OF_DATE",
    "audit_a_share_v09_platform",
    "build_a_share_experiment_registry",
    "evaluate_a_share_simulated_strategy_promotion",
    "run_a_share_automated_experiments",
    "run_a_share_rl_simulated_strategy_lab",
    "run_a_share_v09_daily_platform",
]
