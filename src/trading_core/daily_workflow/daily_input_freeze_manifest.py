"""Freeze daily workflow inputs for a pinned historical as-of date."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id

from .common import BENCHMARK_DATA_SOURCE, DEFAULT_AS_OF_DATE, MARKET_DATA_SOURCE, NOTICE, RISK_PROXY_SOURCE, boundary_markdown, data_quality_path, freeze_path, freeze_report_path, paths_or_default, read_json_file, snapshot_path, source_record, workflow_boundary, write_artifact
from .daily_data_quality_audit import audit_daily_data_quality
from .daily_market_data_snapshot import build_daily_market_data_snapshot


FREEZE_SOURCES = {
    "market_data": MARKET_DATA_SOURCE,
    "benchmark_data": BENCHMARK_DATA_SOURCE,
    "risk_proxy": RISK_PROXY_SOURCE,
    "baseline_strategy_registry": Path("data/strategies/baseline_strategy_registry.json"),
    "baseline_strategy_contract": Path("data/strategies/baseline_strategy_contract.json"),
    "virtual_execution_contract": Path("data/system/virtual_execution_contract.json"),
    "trading_calendar_contract": Path("data/system/ashare_trading_calendar_contract.json"),
    "price_status_contract": Path("data/system/ashare_price_status_contract.json"),
    "lot_position_contract": Path("data/system/ashare_lot_position_contract.json"),
    "cost_contract": Path("data/system/ashare_execution_cost_contract.json"),
}


def build_daily_input_freeze_manifest(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if not snapshot_path(paths, as_of_date).exists():
        build_daily_market_data_snapshot(as_of_date=as_of_date, paths=paths)
    if not data_quality_path(paths, as_of_date).exists():
        audit_daily_data_quality(snapshot=str(snapshot_path(paths, as_of_date)), paths=paths)
    snapshot = read_json_file(snapshot_path(paths, as_of_date))
    quality = read_json_file(data_quality_path(paths, as_of_date))
    manifest_id, generated_at = timestamp_id("DAILY-INPUT-FREEZE-MANIFEST")
    sources = {name: source_record(paths, relative_path) for name, relative_path in FREEZE_SOURCES.items()}
    sources["data_quality_audit"] = source_record(paths, Path(f"data/daily_workflow/audits/daily_data_quality_audit-{as_of_date}.json"))
    sources["daily_market_data_snapshot"] = source_record(paths, Path(f"data/daily_workflow/snapshots/daily_market_data_snapshot-{as_of_date}.json"))
    payload: dict[str, Any] = {
        "manifest_id": manifest_id,
        "as_of_date": as_of_date,
        "latest_available_trading_date": snapshot.get("latest_available_trading_date"),
        "generated_at": generated_at,
        "generated_by_cli": "daily-input-freeze-manifest",
        "data_quality_overall_passed": quality.get("overall_passed") is True,
        "sources": sources,
        "boundary": workflow_boundary("daily_input_freeze_manifest_only"),
    }
    return write_artifact(freeze_path(paths, as_of_date), payload, freeze_report_path(paths, as_of_date), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Input Freeze Manifest - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Sources",
    ]
    lines.extend(f"- {name}: exists={str(item['exists']).lower()} sha256={item['sha256']}" for name, item in payload["sources"].items())
    lines.extend(["", "## Boundary"])
    lines.extend(boundary_markdown("daily input freeze manifest only"))
    lines.append("")
    return "\n".join(lines)
