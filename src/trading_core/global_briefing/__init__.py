"""Global-briefing historical replay harness.

The package is intentionally isolated from run-daily, ML shadow, labels,
experiments, promotion, and broker/live trading surfaces.
"""

from __future__ import annotations

__all__ = [
    "signal_contract",
    "signal_schema",
    "signal_package_validator",
    "replay_bundle_builder",
    "historical_replay_runner",
    "replay_evaluation_report",
    "replay_audit",
]
