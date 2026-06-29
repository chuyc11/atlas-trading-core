"""Research output card."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_research_output_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    outputs = [
        _output(paths, "daily_briefing", paths.outputs_dir / "equity_briefings" / "daily" / as_of_date / "DAILY_STOCK_SELECTION_BRIEFING.md", True),
        _output(paths, "tracking", paths.outputs_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md", True),
        _output(paths, "benchmark", paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date / "A_SHARE_BENCHMARK_SUMMARY.md", False),
        _output(paths, "performance", paths.outputs_dir / "equity_performance" / "daily" / as_of_date / "A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md", False),
        _output(paths, "attribution", paths.outputs_dir / "equity_attribution" / "daily" / as_of_date / "A_SHARE_ATTRIBUTION_SUMMARY.md", False),
        _output(paths, "current_day_run", paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date / "A_SHARE_CURRENT_DAY_RUN_SUMMARY.md", True),
    ]
    return {
        "card_id": "RESEARCH_OUTPUT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "outputs": outputs,
        "briefing_status": _status(outputs, "daily_briefing"),
        "tracking_status": _status(outputs, "tracking"),
        "benchmark_status": _status(outputs, "benchmark"),
        "performance_status": _status(outputs, "performance"),
        "attribution_status": _status(outputs, "attribution"),
        "blocking_reasons": [f"{row['output_id']}_missing" for row in outputs if row["required"] and not row["exists"]],
        "warnings": [f"{row['output_id']}_missing_optional" for row in outputs if not row["required"] and not row["exists"]],
    }


def _output(paths: ProjectPaths, output_id: str, path: Path, required: bool) -> dict[str, Any]:
    exists = path.exists()
    return {
        "output_id": output_id,
        "path": relative(path, paths.project_root),
        "required": required,
        "exists": exists,
        "status": "available" if exists else ("missing_required" if required else "missing_optional"),
    }


def _status(outputs: list[dict[str, Any]], output_id: str) -> str:
    return next(row["status"] for row in outputs if row["output_id"] == output_id)

