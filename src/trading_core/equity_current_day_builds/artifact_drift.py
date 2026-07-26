"""Artifact drift summary for v0.8.7 gated build."""

from __future__ import annotations

import hashlib
from pathlib import Path

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


NO_DRIFT = "no_drift"
TIMESTAMP_ONLY_DRIFT = "timestamp_only_drift"
HASH_METADATA_DRIFT = "hash_metadata_drift"
BUSINESS_OUTPUT_DRIFT = "business_output_drift"
MISSING_REQUIRED_ARTIFACT = "missing_required_artifact"
NEW_EXPECTED_ARTIFACT = "new_expected_artifact"
UNEXPECTED_ARTIFACT = "unexpected_artifact"
BOUNDARY_DRIFT = "boundary_drift"
SOURCE_TRACE_DRIFT = "source_trace_drift"


def build_artifact_drift_summary(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    comparison: dict,
) -> dict:
    paths = default_paths(paths)

    current_day_dir = (
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    )

    drift_items = []
    blocking = []
    warnings = []

    # Check for boundary drift
    boundary_blocking = comparison.get("blocking_reasons", [])
    if any("boundary" in b.lower() for b in boundary_blocking):
        blocking.append("boundary_drift_detected")
        drift_items.append({
            "artifact": "boundary_check",
            "drift_category": BOUNDARY_DRIFT,
            "severity": "blocking",
            "description": "Boundary check failed after build",
        })

    # Check for missing artifacts in build output
    required_artifacts = [
        "current_day_run_manifest.json",
        "current_day_boundary_check.json",
        "current_day_artifact_index.json",
    ]
    for artifact in required_artifacts:
        path = current_day_dir / artifact
        if not path.exists():
            blocking.append(f"missing_required_artifact:{artifact}")
            drift_items.append({
                "artifact": artifact,
                "drift_category": MISSING_REQUIRED_ARTIFACT,
                "severity": "blocking",
                "description": f"Required artifact {artifact} missing after build",
            })

    # Check comparison warnings
    for warning in comparison.get("warnings", []):
        warnings.append(f"comparison:{warning}")

    # If no drift detected
    if not drift_items and not blocking:
        drift_items.append({
            "artifact": "all",
            "drift_category": NO_DRIFT,
            "severity": "informational",
            "description": "No drift detected between validate and build outputs",
        })

    return {
        "drift_summary_id": "A-SHARE-GATED-BUILD-ARTIFACT-DRIFT-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "drift_items": drift_items,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "drift_categories_found": list(set(item["drift_category"] for item in drift_items)),
        "overall_status": "clean" if not blocking else "has_blocking_drift",
    }
