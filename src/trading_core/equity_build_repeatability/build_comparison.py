"""Build-vs-build comparison for repeatability."""

from __future__ import annotations


from trading_core.equity_build_repeatability.deterministic_normalization import normalized_json_hash
from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


BUSINESS_STAGES = {
    "features",
    "scores",
    "selection",
    "portfolios",
    "briefing",
    "tracking",
    "benchmarks",
    "performance",
    "attribution",
}

METADATA_STAGES = {
    "workflow",
    "current_day",
    "gated_build",
    "repeatability",
    "audits",
    "workflow_reports",
    "current_day_reports",
    "briefing_reports",
    "repeatability_reports",
    "audit_reports",
}


def build_build_vs_build_comparison(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    first_snapshot: dict,
    second_snapshot: dict,
    protected_check: dict,
    allow_business_output_drift: bool = False,
) -> dict:
    paths = default_paths(paths)
    first = {entry["artifact_id"]: entry for entry in first_snapshot.get("entries", [])}
    second = {entry["artifact_id"]: entry for entry in second_snapshot.get("entries", [])}

    missing_required = []
    new_expected = []
    unexpected = []
    timestamp_only = []
    metadata_hash = []
    business = []
    boundary_drift = []
    source_trace_drift = []

    for artifact_id in sorted(set(first) | set(second)):
        a = first.get(artifact_id)
        b = second.get(artifact_id)
        if a and not b:
            if a.get("required"):
                missing_required.append(artifact_id)
            continue
        if b and not a:
            if b.get("stage") == "repeatability":
                new_expected.append(artifact_id)
            else:
                unexpected.append(artifact_id)
            continue
        if not a or not b or a.get("sha256") == b.get("sha256"):
            continue
        category = _classify(paths, a, b)
        drift = {"artifact_id": artifact_id, "path": b.get("path"), "stage": b.get("stage"), "category": category}
        if category == "timestamp_only_drift":
            timestamp_only.append(drift)
        elif category == "business_output_drift":
            business.append(drift)
        elif category == "source_trace_drift":
            source_trace_drift.append(drift)
        elif category == "boundary_drift":
            boundary_drift.append(drift)
        else:
            metadata_hash.append(drift)

    blocking = []
    if missing_required:
        blocking.append("missing_required_artifact")
    if unexpected:
        blocking.append("unexpected_artifact")
    if boundary_drift:
        blocking.append("boundary_drift")
    if source_trace_drift:
        blocking.append("source_trace_drift")
    if protected_check.get("protected_path_modifications_detected", False):
        blocking.append("protected_path_drift")
    if business and not allow_business_output_drift:
        blocking.append("business_output_drift")

    drift_categories = ["no_drift"]
    for name, values in [
        ("timestamp_only_drift", timestamp_only),
        ("metadata_hash_drift", metadata_hash),
        ("business_output_drift", business),
        ("missing_required_artifact", missing_required),
        ("new_expected_artifact", new_expected),
        ("unexpected_artifact", unexpected),
        ("boundary_drift", boundary_drift),
        ("protected_path_drift", protected_check.get("protected_path_modifications_detected", False)),
        ("source_trace_drift", source_trace_drift),
    ]:
        if values:
            drift_categories.append(name)
    if len(drift_categories) > 1:
        drift_categories.remove("no_drift")

    return {
        "comparison_id": "A-SHARE-BUILD-VS-BUILD-COMPARISON",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": "build_from_existing_data",
        "comparison_completed": True,
        "comparison_categories": [
            "workflow_audit_status",
            "stage_status",
            "artifact_inventory",
            "summary_values",
            "warnings",
            "source_trace",
            "boundary",
            "protected_path_state",
            "business_outputs",
            "timestamp_fields",
            "hash_fields",
        ],
        "first_artifact_count": first_snapshot.get("artifact_count", 0),
        "second_artifact_count": second_snapshot.get("artifact_count", 0),
        "missing_required_artifacts": missing_required,
        "new_expected_artifacts": new_expected,
        "unexpected_artifacts": unexpected,
        "timestamp_only_drift": timestamp_only,
        "metadata_hash_drift": metadata_hash,
        "business_output_drift": business,
        "boundary_drift": bool(boundary_drift),
        "protected_path_drift": protected_check.get("protected_path_modifications_detected", False),
        "source_trace_drift": bool(source_trace_drift),
        "timestamp_only_drift_count": len(timestamp_only),
        "metadata_hash_drift_count": len(metadata_hash),
        "business_output_drift_count": len(business),
        "missing_required_artifact_count": len(missing_required),
        "drift_categories_found": sorted(set(drift_categories)),
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }


def _classify(paths: ProjectPaths, first: dict, second: dict) -> str:
    rel = second.get("path", "")
    stage = second.get("stage")
    normalized_first = first.get("normalized_sha256")
    normalized_second = second.get("normalized_sha256")
    if normalized_first and normalized_first == normalized_second:
        if rel.endswith(".parquet"):
            return "metadata_hash_drift"
        return "timestamp_only_drift"
    if "boundary" in rel:
        if _normalized_equal(paths, first, second):
            return "timestamp_only_drift"
        return "boundary_drift"
    if "source_trace" in rel:
        if _normalized_equal(paths, first, second):
            return "timestamp_only_drift"
        return "source_trace_drift"
    if _normalized_equal(paths, first, second):
        return "timestamp_only_drift"
    if stage in BUSINESS_STAGES:
        return "business_output_drift"
    if stage in METADATA_STAGES:
        return "metadata_hash_drift"
    return "metadata_hash_drift"


def _normalized_equal(paths: ProjectPaths, first: dict, second: dict) -> bool:
    first_path = paths.project_root / first.get("path", "")
    second_path = paths.project_root / second.get("path", "")
    if first_path.suffix.lower() != ".json" or second_path.suffix.lower() != ".json":
        return False
    if not first_path.exists() or not second_path.exists():
        return False
    return normalized_json_hash(first_path.read_text(encoding="utf-8", errors="ignore")) == normalized_json_hash(
        second_path.read_text(encoding="utf-8", errors="ignore")
    )
