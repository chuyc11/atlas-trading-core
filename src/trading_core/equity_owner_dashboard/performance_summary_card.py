"""Performance summary card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_performance_summary_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    summary = load_json(paths.data_dir / "equity_performance" / "daily" / as_of_date / "performance_summary.json")
    status = "missing_optional"
    if summary:
        status = "available" if summary.get("sufficient_history") else "limited_history"
    return {
        "card_id": "PERFORMANCE_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": status,
        "observation_counts": summary.get("portfolio_observation_count", {}),
        "minimum_required_observations": summary.get("minimum_required_observations"),
        "sufficient_history": summary.get("sufficient_history"),
        "first_day_initialization": summary.get("first_day_initialization"),
        "performance_not_yet_observed": summary.get("performance_not_yet_observed"),
        "portfolios": summary.get("portfolios", {}),
        "limited_history_disclaimer": "observation count below minimum; do not imply performance effectiveness",
        "warnings": list(summary.get("warnings", [])) if summary else ["performance_missing_optional"],
    }

