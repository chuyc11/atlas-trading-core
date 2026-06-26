"""Build the day1 data and reproducibility appendix."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import build_simple_markdown, load_day1_owner_report_context, paths_or_default, report_boundary, source_and_artifact_hashes, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_data_reproducibility_appendix(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    snapshot = context["payloads"].get("day1_input_snapshot", {})
    manifest = context["payloads"].get("day1_reproducibility_manifest", {})
    hashes = source_and_artifact_hashes(context)
    payload: dict[str, Any] = {
        "appendix_id": "FORWARD-DRY-RUN-DAY1-DATA-REPRODUCIBILITY-APPENDIX",
        "day_index": 1,
        "day1_as_of_date": snapshot.get("as_of_date"),
        "market_data_source": snapshot.get("source_hashes", {}).get("market_data", {}).get("path"),
        "benchmark_source": snapshot.get("source_hashes", {}).get("benchmark_data", {}).get("path"),
        "risk_proxy_source": snapshot.get("source_hashes", {}).get("risk_proxy", {}).get("path"),
        "source_hashes": hashes["source_hashes"],
        "source_artifact_hashes": hashes["source_artifact_hashes"],
        "artifact_hashes": hashes["artifact_hashes"],
        "ledger_hash": hashes["ledger_hash"],
        "git_tag": manifest.get("baseline_tag"),
        "git_commit": manifest.get("current_head") or manifest.get("tag_commit"),
        "python_version": manifest.get("python_version"),
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "determinism_policy": manifest.get("determinism_policy", {"hashes_exclude_generated_at": True}),
        "non_deterministic_fields_policy": manifest.get("non_deterministic_fields_policy", {}),
        "boundary": report_boundary("data_reproducibility_appendix_only"),
    }
    lines = [
        f"- day1_as_of_date: {payload['day1_as_of_date']}",
        f"- market_data_source: {payload['market_data_source']}",
        f"- benchmark_source: {payload['benchmark_source']}",
        f"- risk_proxy_source: {payload['risk_proxy_source']}",
        f"- git_tag: {payload['git_tag']}",
        f"- git_commit: {payload['git_commit']}",
        f"- python_version: {payload['python_version']}",
        "- external_api_called: false",
        "- real_time_market_data_downloaded: false",
        f"- ledger_hash: {payload['ledger_hash']}",
    ]
    return write_report_artifact(paths, "day1_data_reproducibility_appendix.json", payload, "DAY1_DATA_REPRODUCIBILITY_APPENDIX.md", build_simple_markdown("Day1 Data Reproducibility Appendix", lines, payload))
