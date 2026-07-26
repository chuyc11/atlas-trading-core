"""Baseline strategy pack completeness summary."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import write_json_markdown

from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    RESEARCH_NOTICE,
    STRATEGY_IDS,
    benchmark_path,
    paths_or_default,
    preview_path,
    replay_summary_path,
    report_path,
    research_boundary,
    signal_path,
)


def build_baseline_strategy_pack_summary(
    *,
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_path = paths.data_dir / "strategies" / "baseline_strategy_contract.json"
    registry_path = paths.data_dir / "strategies" / "baseline_strategy_registry.json"
    benchmark = benchmark_path(paths, start_date, end_date)
    warnings = []
    strategies = {}
    for strategy_id in STRATEGY_IDS:
        row = {
            "contract_exists": contract_path.exists(),
            "registry_exists": registry_path.exists(),
            "signals_exist": signal_path(paths, strategy_id, start_date, end_date).exists(),
            "order_preview_exists": preview_path(paths, strategy_id, start_date, end_date).exists(),
            "replay_exists": replay_summary_path(paths, strategy_id, start_date, end_date).exists(),
            "benchmark_comparison_exists": benchmark.exists(),
            "report_exists": report_path(paths, strategy_id, start_date, end_date).exists(),
        }
        if not row["report_exists"]:
            warnings.append(f"{strategy_id} report missing")
        row["complete"] = all(row.values())
        strategies[strategy_id] = row
    all_complete = all(row["complete"] for row in strategies.values())
    payload: dict[str, Any] = {
        "summary_id": f"BASELINE-STRATEGY-PACK-SUMMARY-{start_date}-{end_date}",
        "start_date": start_date,
        "end_date": end_date,
        "strategies": strategies,
        "strategy_count": len(strategies),
        "strategies_complete": sum(1 for row in strategies.values() if row["complete"]),
        "all_strategies_complete": all_complete,
        "warnings": warnings,
        "promotion_triggered": False,
        "forward_dry_run_started": False,
        "run_daily_called": False,
        "main_ledger_written": False,
        "boundary": research_boundary("baseline_strategy_pack_summary_only"),
    }
    json_path = paths.data_dir / "strategies" / "baseline_strategy_pack_summary.json"
    md_path = paths.outputs_dir / "strategies" / "BASELINE_STRATEGY_PACK_SUMMARY.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload, paths))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_markdown(payload: dict[str, Any], paths: ProjectPaths) -> str:
    lines = [
        "# Baseline Strategy Pack Summary",
        "",
        RESEARCH_NOTICE,
        "",
        "## Coverage",
    ]
    for strategy_id, row in payload["strategies"].items():
        lines.append(f"- {strategy_id}: complete={str(row['complete']).lower()}")
    lines.extend(
        [
            "",
            "## Summary",
            f"- strategy_count: {payload['strategy_count']}",
            f"- strategies_complete: {payload['strategies_complete']}",
            f"- all_strategies_complete: {str(payload['all_strategies_complete']).lower()}",
            "",
            "## Boundary",
            "- baseline strategy pack summary only",
            "- run-daily not called",
            "- forward dry-run not started",
            "- main ledger not written",
            "- promotion not triggered",
            "",
        ]
    )
    return "\n".join(lines)

