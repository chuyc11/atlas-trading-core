"""Module reliability baseline."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


MODULES = ["data_refresh", "current_day_research_run", "owner_dashboard", "owner_monitoring", "owner_remediation", "ops_center"]


def build_ops_module_reliability_baseline(*, as_of_date: str, module_matrix: dict[str, Any], records: list[dict[str, Any]], minimum_required_observations: int) -> dict[str, Any]:
    latest_rows = {row["module_id"]: row for row in module_matrix.get("rows", [])}
    count = len(records)
    enough = count >= minimum_required_observations
    modules = []
    for module_id in MODULES:
        latest = latest_rows.get(module_id, {})
        passed = latest.get("status") in {"passed", "passed_with_warnings"}
        modules.append(
            {
                "module_id": module_id,
                "observation_count": count,
                "pass_count": 1 if passed and count else 0,
                "warning_count": int(latest.get("warning_count", 0)),
                "fail_count": 0 if passed else (1 if count else 0),
                "blocking_count": int(latest.get("blocking_count", 0)),
                "latest_status": latest.get("status", "missing"),
                "reliability_rate": (1.0 if passed else 0.0) if enough else None,
                "trend_status": "available" if enough else "insufficient_history",
            }
        )
    return {"baseline_id": "A-SHARE-OPS-MODULE-RELIABILITY-BASELINE", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "modules": modules}
