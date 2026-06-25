"""Daily data quality audit for research signal generation."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from trading_core.execution.trading_calendar_contract import default_calendar
from trading_core.storage.file_paths import ProjectPaths

from .common import NOTICE, boundary_markdown, data_quality_path, data_quality_report_path, paths_or_default, read_json_file, snapshot_path, workflow_boundary, write_artifact


def audit_daily_data_quality(*, snapshot: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    snapshot_file = _resolve_snapshot(snapshot, paths)
    snapshot_payload = read_json_file(snapshot_file)
    as_of = str(snapshot_payload.get("as_of_date") or _date_from_path(snapshot_file) or "2024-12-31")
    sections = {
        "snapshot": _passed(bool(snapshot_payload), "snapshot missing"),
        "latest_available_trading_date": _passed(bool(snapshot_payload.get("latest_available_trading_date")), "latest available trading date missing"),
        "as_of_date_covered": _passed(snapshot_payload.get("as_of_date") == as_of, "as_of_date not covered"),
        "universe_coverage": _symbols_section(snapshot_payload),
        "benchmarks": _benchmarks_section(snapshot_payload),
        "risk_proxy": _passed(snapshot_payload.get("risk_proxy_available") is True, "risk proxy missing"),
        "trading_day": _passed(default_calendar().is_trading_day(as_of, "SSE"), "as_of_date is not expected trading day"),
        "sources": _passed(all(item.get("exists") for item in snapshot_payload.get("source_records", {}).values()), "source missing"),
        "boundary": _passed(snapshot_payload.get("boundary", {}).get("external_api_called") is False and snapshot_payload.get("boundary", {}).get("run_daily_called") is False, "boundary failed"),
    }
    warnings = []
    benchmark_missing = [name for name, item in snapshot_payload.get("benchmarks", {}).items() if not item.get("available")]
    if benchmark_missing:
        warnings.append({"type": "benchmark_missing_for_pinned_date", "benchmarks": benchmark_missing, "severity": "warning"})
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    symbols = snapshot_payload.get("symbols", {})
    payload: dict[str, Any] = {
        "as_of_date": as_of,
        "snapshot_path": snapshot_file.as_posix(),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "summary": {
            "symbols_total": len(symbols),
            "symbols_complete": sum(1 for item in symbols.values() if item.get("available") and item.get("close_available") and item.get("volume_available")),
            "missing_symbols": sum(1 for item in symbols.values() if not item.get("available")),
            "stale_symbols": sum(1 for item in symbols.values() if item.get("stale")),
            "benchmark_available": any(item.get("available") for item in snapshot_payload.get("benchmarks", {}).values()),
            "risk_proxy_available": snapshot_payload.get("risk_proxy_available") is True,
        },
        "sections": sections,
        "boundary": workflow_boundary("data_quality_audit_only"),
    }
    return write_artifact(data_quality_path(paths, as_of), payload, data_quality_report_path(paths, as_of), build_markdown(payload))


def _resolve_snapshot(snapshot: str | None, paths: ProjectPaths) -> Path:
    if snapshot:
        path = Path(snapshot)
        return path if path.is_absolute() else paths.project_root / path
    return snapshot_path(paths, "2024-12-31")


def _date_from_path(path: Path) -> str | None:
    match = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
    return match.group(0) if match else None


def _passed(condition: bool, issue: str) -> dict[str, Any]:
    return {"passed": condition, "issues": [] if condition else [issue]}


def _symbols_section(snapshot_payload: dict[str, Any]) -> dict[str, Any]:
    issues = []
    for symbol, item in snapshot_payload.get("symbols", {}).items():
        if not item.get("available"):
            issues.append(f"{symbol} missing")
        if not item.get("close_available"):
            issues.append(f"{symbol} close missing")
        if not item.get("volume_available"):
            issues.append(f"{symbol} volume missing")
    return {"passed": not issues, "issues": issues}


def _benchmarks_section(snapshot_payload: dict[str, Any]) -> dict[str, Any]:
    available = [name for name, item in snapshot_payload.get("benchmarks", {}).items() if item.get("available")]
    return {"passed": bool(available), "issues": [] if available else ["no benchmark available"]}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Data Quality Audit - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        f"- warnings={len(payload['warnings'])}",
        "",
        "## Boundary",
    ]
    lines.extend(boundary_markdown("data quality audit only"))
    lines.append("")
    return "\n".join(lines)
