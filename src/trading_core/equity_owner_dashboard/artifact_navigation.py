"""Artifact navigation index for owner dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import artifact_record
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_artifact_navigation_index(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    items = [
        ("data_refresh_summary", "数据刷新汇总", "data_refresh", paths.data_dir / "equity_data_refresh" / "daily" / as_of_date / "data_refresh_summary.json", "high"),
        ("current_day_run_summary", "当前日运行汇总", "current_day", paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date / "A_SHARE_CURRENT_DAY_RUN_SUMMARY.md", "high"),
        ("daily_briefing", "每日研究简报", "briefing", paths.outputs_dir / "equity_briefings" / "daily" / as_of_date / "DAILY_STOCK_SELECTION_BRIEFING.md", "high"),
        ("tracking_summary", "虚拟组合跟踪", "tracking", paths.outputs_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md", "high"),
        ("benchmark_summary", "Benchmark 汇总", "benchmark", paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date / "A_SHARE_BENCHMARK_SUMMARY.md", "medium"),
        ("performance_summary", "多日绩效状态", "performance", paths.outputs_dir / "equity_performance" / "daily" / as_of_date / "A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md", "medium"),
        ("attribution_summary", "归因与风险诊断", "attribution", paths.outputs_dir / "equity_attribution" / "daily" / as_of_date / "A_SHARE_ATTRIBUTION_SUMMARY.md", "medium"),
        ("current_day_audit", "当前日运行审计", "audit", paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json", "diagnostic"),
        ("data_refresh_audit", "数据刷新审计", "audit", paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json", "diagnostic"),
        ("workflow_audit", "研究 workflow 审计", "audit", paths.data_dir / "equity_data_quality" / "a_share_daily_workflow_audit.json", "diagnostic"),
    ]
    artifacts = []
    for artifact_id, label, category, path, priority in items:
        row = artifact_record(paths, path, label_zh=label, category=category, owner_priority=priority)
        row["artifact_id"] = artifact_id
        artifacts.append(row)
    return {
        "navigation_id": "A-SHARE-OWNER-ARTIFACT-NAVIGATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
    }

