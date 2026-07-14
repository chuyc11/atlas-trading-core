"""Source tracing for A-share daily stock selection briefings."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from trading_core.equity_briefings.briefing_config import SOURCE_TRACE_SECTION_KEYS, TARGET_VERSION
from trading_core.equity_briefings.briefing_inputs import BriefingInputs, briefing_data_dir, briefing_output_dir
from trading_core.equity_data_quality.common import sha256_file, write_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_briefing_source_trace(paths: ProjectPaths, inputs: BriefingInputs, generated_at: str) -> dict[str, Any]:
    section_sources: dict[str, list[Path]] = {
        "executive_summary": [
            inputs.candidate_manifest_path,
            inputs.score_manifest_path,
            inputs.feature_manifest_path,
            inputs.portfolio_manifest_path,
            inputs.portfolio_dir / "portfolio_industry_exposure.json",
            inputs.portfolio_dir / "portfolio_risk_liquidity_summary.json",
        ],
        "long_candidates_top10": [inputs.candidate_dir / "long_candidates.json"],
        "mid_candidates_top10": [inputs.candidate_dir / "mid_candidates.json"],
        "short_candidates_top10": [inputs.candidate_dir / "short_candidates.json"],
        "multi_horizon_candidates": [inputs.candidate_dir / "multi_horizon_candidates.json"],
        "risk_downgraded_candidates": [inputs.candidate_dir / "risk_downgraded_candidates.json"],
        "virtual_portfolio_summary": [
            inputs.portfolio_dir / "long_virtual_portfolio.json",
            inputs.portfolio_dir / "mid_virtual_portfolio.json",
            inputs.portfolio_dir / "short_virtual_portfolio.json",
            inputs.portfolio_dir / "portfolio_weight_summary.json",
        ],
        "industry_exposure_summary": [inputs.portfolio_dir / "portfolio_industry_exposure.json"],
        "risk_liquidity_summary": [inputs.portfolio_dir / "portfolio_risk_liquidity_summary.json"],
        "audit_status": [
            paths.data_dir / "equity_data_quality" / "a_share_candidate_generation_audit.json",
            paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json",
            paths.data_dir / "equity_data_quality" / "a_share_multi_horizon_feature_audit.json",
            paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_construction_audit.json",
        ],
        "do_not_misread": [inputs.portfolio_manifest_path, inputs.candidate_manifest_path],
        "next_tracking_actions": [inputs.portfolio_manifest_path],
    }
    sections = {}
    for key in SOURCE_TRACE_SECTION_KEYS:
        paths_for_section = section_sources[key]
        source_records = [_source_record(paths, path, inputs.as_of_date) for path in paths_for_section]
        date_aligned = all(record.get("as_of_date_matches", True) for record in source_records)
        sections[key] = {
            "source_paths": [relative(path, paths.project_root) for path in paths_for_section],
            "sources": source_records,
            "date_aligned": date_aligned,
            "complete": all(path.exists() for path in paths_for_section) and date_aligned,
        }
    return {
        "trace_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "sections": sections,
        "source_trace_complete": all(section["complete"] for section in sections.values()),
    }


def write_briefing_source_trace(paths: ProjectPaths, as_of_date: str, trace: dict[str, Any]) -> dict[str, str]:
    data_dir = briefing_data_dir(paths, as_of_date)
    output_dir = briefing_output_dir(paths, as_of_date)
    json_path = data_dir / "briefing_source_trace.json"
    report_path = output_dir / "BRIEFING_SOURCE_TRACE.md"
    write_json(json_path, trace)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_source_trace_report(trace), encoding="utf-8")
    return {"briefing_source_trace": str(json_path), "briefing_source_trace_report": str(report_path)}


def render_source_trace_report(trace: dict[str, Any]) -> str:
    lines = [
        "# Briefing Source Trace",
        "",
        f"- target_version: {trace['target_version']}",
        f"- as_of_date: {trace['as_of_date']}",
        f"- source_trace_complete: {str(trace['source_trace_complete']).lower()}",
        "",
        "| Section | Complete | Date Aligned | Source Paths / SHA256 |",
        "|---|---:|---:|---|",
    ]
    for section, record in trace["sections"].items():
        sources = "<br>".join(f"{source['path']} ({source.get('sha256') or 'missing'})" for source in record.get("sources", []))
        lines.append(f"| {section} | {str(record['complete']).lower()} | {str(record.get('date_aligned', True)).lower()} | {sources} |")
    return "\n".join(lines) + "\n"


def _source_record(paths: ProjectPaths, path: Path, expected_as_of_date: str) -> dict[str, Any]:
    source_as_of_date = None
    if path.exists() and path.suffix.lower() == ".json":
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                source_as_of_date = value.get("as_of_date")
        except (json.JSONDecodeError, OSError):
            source_as_of_date = None
    record = {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path),
    }
    if "equity_data_quality" in path.parts:
        record["as_of_date"] = source_as_of_date
        record["as_of_date_matches"] = source_as_of_date == expected_as_of_date
    return record
