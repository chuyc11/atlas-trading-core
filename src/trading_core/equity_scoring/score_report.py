"""Markdown reports for A-share scoring."""

from __future__ import annotations

from typing import Any

from trading_core.equity_scoring.component_scores import score_output_dir
from trading_core.storage.file_paths import ProjectPaths


def write_score_reports(paths: ProjectPaths, as_of_date: str, summary: dict[str, Any], distribution: dict[str, Any]) -> dict[str, str]:
    output_dir = score_output_dir(paths, as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "SCORING_SUMMARY.md"
    distribution_path = output_dir / "SCORE_DISTRIBUTION_REPORT.md"
    summary_lines = [
        "# A-Share Scoring Summary",
        "",
        f"- as_of_date: {as_of_date}",
        f"- strict_tradable_count: {summary['strict_tradable_count']}",
        f"- scored_symbols: {summary['scored_symbols']}",
        f"- warnings: {len(summary.get('warnings', []))}",
        "- scoring only: true",
        "- scores generated: true",
        "- candidates generated: false",
        "- watchlists generated: false",
        "- virtual portfolios generated: false",
        "",
        "Scores are cross-sectional research scores. They are not recommendations, buy/sell signals, portfolio actions, profit guarantees, or live-trading readiness claims.",
    ]
    distribution_lines = [
        "# A-Share Score Distribution",
        "",
        f"- as_of_date: {as_of_date}",
        "- percentile_convention: 0_to_100",
        "- confidence_convention: 0_to_1",
        "",
    ]
    for score_name, item in distribution["scores"].items():
        distribution_lines.append(f"## {score_name}")
        distribution_lines.append(f"- count: {item['count']}")
        distribution_lines.append(f"- min: {item['min']}")
        distribution_lines.append(f"- max: {item['max']}")
        distribution_lines.append(f"- mean: {item['mean']}")
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    distribution_path.write_text("\n".join(distribution_lines), encoding="utf-8")
    return {"scoring_summary_report_path": str(summary_path), "score_distribution_report_path": str(distribution_path)}
