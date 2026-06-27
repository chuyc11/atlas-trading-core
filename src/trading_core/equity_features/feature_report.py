"""Markdown reports for A-share multi-horizon feature engineering."""

from __future__ import annotations

from typing import Any

from trading_core.equity_features.feature_inputs import feature_output_dir
from trading_core.storage.file_paths import ProjectPaths


def write_feature_reports(paths: ProjectPaths, as_of_date: str, summary: dict[str, Any], coverage: dict[str, Any]) -> dict[str, str]:
    output_dir = feature_output_dir(paths, as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "FEATURE_GENERATION_SUMMARY.md"
    coverage_path = output_dir / "FEATURE_FIELD_COVERAGE.md"
    summary_lines = [
        "# A-Share Multi-Horizon Feature Generation Summary",
        "",
        f"- as_of_date: {as_of_date}",
        f"- strict_tradable_count: {summary['strict_tradable_count']}",
        f"- warnings: {len(summary.get('warnings', []))}",
        "- features only: true",
        "- scores generated: false",
        "- candidates generated: false",
        "- virtual portfolios generated: false",
        "",
        "## Feature Groups",
    ]
    for group, item in summary["feature_groups"].items():
        summary_lines.append(f"- {group}: symbols={item['symbols']}, fields={item['fields']}")
    summary_lines.extend(["", "These features are inputs for a future scoring stage. They are not recommendations."])
    coverage_lines = ["# A-Share Feature Field Coverage", "", f"- as_of_date: {as_of_date}", ""]
    for group, item in coverage["groups"].items():
        coverage_lines.append(f"## {group}")
        coverage_lines.append(f"- symbol_coverage: {item['symbol_coverage']}")
        coverage_lines.append(f"- mandatory_field_coverage: {item['mandatory_field_coverage']}")
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    coverage_path.write_text("\n".join(coverage_lines), encoding="utf-8")
    return {"summary_report_path": str(summary_path), "field_coverage_report_path": str(coverage_path)}

