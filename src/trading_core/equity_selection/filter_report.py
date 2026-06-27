"""Markdown report writers for A-share tradable universe artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_selection.filter_config import TARGET_VERSION
from trading_core.equity_selection.filter_inputs import selection_output_dir
from trading_core.storage.file_paths import ProjectPaths


def write_tradable_universe_reports(paths: ProjectPaths, as_of_date: str, payload: dict[str, Any]) -> dict[str, str]:
    output_dir = selection_output_dir(paths, as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "TRADABLE_UNIVERSE_REPORT.md"
    breakdown_path = output_dir / "FILTER_REASON_BREAKDOWN.md"
    counts = payload["counts"]
    thresholds = payload["config"]["thresholds"]
    top_reasons = sorted(payload["reason_breakdown"]["reason_counts"].items(), key=lambda item: item[1], reverse=True)[:15]
    report_lines = [
        "# A-Share Tradable Universe Report",
        "",
        f"- target_version: {TARGET_VERSION}",
        f"- as_of_date: {as_of_date}",
        f"- strict_tradable_count: {counts['strict_tradable_count']}",
        f"- caution_count: {counts['caution_count']}",
        f"- excluded_count: {counts['excluded_count']}",
        f"- unknown_status_count: {counts['unknown_status_count']}",
        f"- include_caution: {str(payload['config']['include_caution']).lower()}",
        "- stock scores generated: false",
        "- candidates generated: false",
        "- watchlist generated: false",
        "- virtual portfolios generated: false",
        "- broker connected: false",
        "- real orders placed: false",
        "- live trading ready: false",
        "",
        "## Thresholds",
        *(f"- {key}: {value}" for key, value in thresholds.items()),
        "",
        "## Top Exclusion Reasons",
        *(f"- {reason}: {count}" for reason, count in top_reasons),
        "",
        "strict_tradable_universe is the default input for future scoring. caution_universe is observation-only unless a future command explicitly allows it.",
        "",
    ]
    breakdown_lines = [
        "# A-Share Tradable Universe Filter Reason Breakdown",
        "",
        f"- as_of_date: {as_of_date}",
        f"- input_symbols: {payload['reason_breakdown']['input_symbols']}",
        "",
        "## Reason Counts",
        *(f"- {reason}: {count}" for reason, count in sorted(payload["reason_breakdown"]["reason_counts"].items(), key=lambda item: item[1], reverse=True)),
        "",
        "## Stage Counts",
        *(f"- {stage}: {count}" for stage, count in sorted(payload["reason_breakdown"]["stage_counts"].items())),
        "",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    breakdown_path.write_text("\n".join(breakdown_lines), encoding="utf-8")
    return {"report_path": str(report_path), "breakdown_report_path": str(breakdown_path)}

