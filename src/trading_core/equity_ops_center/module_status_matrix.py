"""Module status matrix for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


def build_ops_module_status_matrix(*, as_of_date: str, availability: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for module in availability.get("modules", []):
        blocking_count = len(module.get("blocking_reasons", []))
        warning_count = int(module.get("warning_count", 0))
        rows.append(
            {
                "module_id": module["module_id"],
                "audit_passed": module["audit_passed"],
                "blocking_count": blocking_count,
                "warning_count": warning_count,
                "boundary_clean": module["boundary_passed"],
                "source_trace_available": bool(module.get("source_trace_path")),
                "summary_available": bool(module.get("summary_path")),
                "recommended_next_version": module.get("recommended_next_version"),
                "status": _status(module, blocking_count, warning_count),
            }
        )
    return {
        "matrix_id": "A-SHARE-DAILY-OPS-CENTER-MODULE-STATUS-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "rows": rows,
        "required_modules_passed": all(row["audit_passed"] and row["boundary_clean"] for row in rows),
    }


def _status(module: dict[str, Any], blocking_count: int, warning_count: int) -> str:
    if not module.get("available"):
        return "missing"
    if blocking_count:
        return "blocked"
    if not module.get("audit_passed"):
        return "failed"
    if warning_count:
        return "passed_with_warnings"
    return "passed"
