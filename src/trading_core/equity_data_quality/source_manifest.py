"""Build A-share data source manifest."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import PROTECTED_BOUNDARY, TARGET_VERSION, data_quality_dir, markdown_boundary, write_report
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot, provider_status
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_a_share_data_source_manifest(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    status = provider_status(snapshot)
    payload: dict[str, Any] = {
        "manifest_id": "A-SHARE-DATA-SOURCE-MANIFEST",
        "target_version": TARGET_VERSION,
        **status,
        "selected_provider": snapshot.get("provider", ""),
        "rows_available": len(snapshot.get("rows", [])),
        "raw_total": snapshot.get("raw_total"),
        "raw_coverage_ratio": snapshot.get("raw_coverage_ratio"),
        "provider_reason": snapshot.get("provider_reason", ""),
        "warnings": [snapshot["provider_reason"]] if snapshot.get("provider_reason") else [],
        "external_research_used_as_reference": True,
        "third_party_code_merged_into_main_flow": False,
        "data_written_to_local_store": bool(snapshot.get("rows")),
        "external_api_called": bool(snapshot.get("external_api_called")),
        "real_time_market_data_downloaded": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "boundary": dict(PROTECTED_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_data_source_manifest.json"
    report_path = paths.outputs_dir / "equity_data_quality" / "A_SHARE_DATA_SOURCE_MANIFEST.md"
    lines = [
        "# A-Share Data Source Manifest",
        "",
        f"- selected_provider: {payload['selected_provider']}",
        f"- rows_available: {payload['rows_available']}",
        f"- raw_total: {payload['raw_total']}",
        f"- raw_coverage_ratio: {payload['raw_coverage_ratio']}",
        f"- provider_reason: {payload['provider_reason']}",
        f"- providers_attempted: {payload['providers_attempted']}",
        f"- providers_succeeded: {payload['providers_succeeded']}",
        f"- external_api_called: {str(payload['external_api_called']).lower()}",
        "- real_time_market_data_downloaded: false",
        "- broker_connected: false",
        "- real_orders_placed: false",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))
