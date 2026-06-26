"""Build the v0.6.3 day1 artifact manifest required for continuation."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import day_json, day_report, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import (
    BASELINE_TAG,
    DAY1_CORE_ARTIFACTS,
    artifact_hashes,
    artifact_records,
    day1_core_status,
    markdown_boundary,
    standard_boundary,
    paths_or_default,
)
from trading_core.storage.file_paths import ProjectPaths


def build_day1_artifact_manifest(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    core = day1_core_status(paths)
    records = artifact_records(paths)
    missing_required = [record["path"] for record in records if record["required"] and not record["exists"]]
    blocking = list(core["blocking_reasons"])
    blocking.extend(f"missing_required_artifact: {relative}" for relative in missing_required if f"missing_day1_core_artifact: {relative}" not in blocking)
    payload: dict[str, Any] = {
        "manifest_id": "FORWARD-DRY-RUN-DAY1-ARTIFACT-MANIFEST",
        "day_index": 1,
        "baseline_tag": BASELINE_TAG,
        "required_artifacts_total": len(DAY1_CORE_ARTIFACTS),
        "required_artifacts_present": len(DAY1_CORE_ARTIFACTS) - len(missing_required),
        "missing_required_artifacts": missing_required,
        "artifacts": records,
        "artifact_hashes": artifact_hashes(records),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "boundary": standard_boundary("manifest_only"),
    }
    return write_artifact(day_json(paths, "day1_artifact_manifest.json"), payload, day_report(paths, "DAY1_ARTIFACT_MANIFEST.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Artifact Manifest",
        "",
        f"- required_artifacts_total: {payload['required_artifacts_total']}",
        f"- required_artifacts_present: {payload['required_artifacts_present']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        "",
        "## Artifacts",
    ]
    lines.extend(f"- {item['name']}: exists={str(item['exists']).lower()} sha256={item['sha256']}" for item in payload["artifacts"])
    lines.extend(["", "## Boundary", *markdown_boundary(), ""])
    return "\n".join(lines)

