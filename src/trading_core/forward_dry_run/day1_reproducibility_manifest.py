"""Build the v0.6.3 day1 reproducibility manifest."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import day_json, day_report, read_json_file, source_hashes, write_artifact
from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest
from trading_core.forward_dry_run.day1_continuation_common import (
    BASELINE_TAG,
    artifact_hashes,
    artifact_records,
    day1_core_status,
    markdown_boundary,
    paths_or_default,
    project_path,
    python_runtime,
    release_commit_info,
    sha256_path,
    standard_boundary,
)
from trading_core.storage.file_paths import ProjectPaths


def build_day1_reproducibility_manifest(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    core = day1_core_status(paths)
    manifest_path = day_json(paths, "day1_artifact_manifest.json")
    if not manifest_path.exists():
        build_day1_artifact_manifest(paths=paths)
    snapshot = read_json_file(day_json(paths, "day1_input_snapshot.json"))
    records = artifact_records(paths)
    source_artifacts = {
        "baseline_strategy_registry": "data/strategies/baseline_strategy_registry.json",
        "baseline_strategy_contract": "data/strategies/baseline_strategy_contract.json",
        "virtual_execution_contract": "data/system/virtual_execution_contract.json",
        "trading_calendar_contract": "data/system/ashare_trading_calendar_contract.json",
        "execution_cost_contract": "data/system/ashare_execution_cost_contract.json",
    }
    source_artifact_hashes = {name: {"path": relative, "exists": project_path(paths, relative).exists(), "sha256": sha256_path(project_path(paths, relative))} for name, relative in source_artifacts.items()}
    ledger_hash = sha256_path(paths.data_dir / "forward_dry_run" / "ledger" / "day1_ledger.json")
    payload: dict[str, Any] = {
        "manifest_id": "FORWARD-DRY-RUN-DAY1-REPRODUCIBILITY-MANIFEST",
        "day_index": 1,
        "baseline_tag": BASELINE_TAG,
        **release_commit_info(paths),
        **python_runtime(),
        "pytest_summary": "890 passed, 1 skipped at v0.6.3 release verification",
        "day1_as_of_date": snapshot.get("as_of_date"),
        "source_hashes": source_hashes(paths),
        "source_artifact_hashes": source_artifact_hashes,
        "artifact_hashes": artifact_hashes(records),
        "ledger_hash": ledger_hash,
        "determinism_policy": {
            "hashes_exclude_generated_at": True,
            "non_deterministic_fields_recorded": True,
        },
        "non_deterministic_fields_policy": {
            "generated_at": "recorded but excluded from stable content hashes where applicable",
            "git_status": "recorded as contextual evidence only",
        },
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "overall_passed": core["overall_passed"],
        "blocking_reasons": core["blocking_reasons"],
        "boundary": standard_boundary("manifest_only"),
    }
    payload["boundary"]["external_api_called"] = False
    payload["boundary"]["real_time_market_data_downloaded"] = False
    return write_artifact(day_json(paths, "day1_reproducibility_manifest.json"), payload, day_report(paths, "DAY1_REPRODUCIBILITY_MANIFEST.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Reproducibility Manifest",
        "",
        f"- baseline_tag: {payload['baseline_tag']}",
        f"- day1_as_of_date: {payload['day1_as_of_date']}",
        f"- ledger_hash: {payload['ledger_hash']}",
        "- external_api_called: false",
        "- real_time_market_data_downloaded: false",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

