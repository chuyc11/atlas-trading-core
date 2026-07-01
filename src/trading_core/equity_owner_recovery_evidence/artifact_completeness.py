"""Artifact completeness evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_artifact_completeness_evidence(*, as_of_date: str = DEFAULT_AS_OF_DATE, required_paths: dict[str, Path]) -> dict[str, Any]:
    required = sorted(required_paths)
    present = sorted(key for key, path in required_paths.items() if path.exists())
    missing = sorted(set(required) - set(present))
    ratio = len(present) / len(required) if required else 1.0
    return {
        "evidence_id": "A-SHARE-ARTIFACT-COMPLETENESS-EVIDENCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_items": required,
        "present_items": present,
        "missing_items": missing,
        "completeness_ratio": ratio,
        "quality_grade": "audit_verified" if ratio == 1 else "partial" if ratio else "none",
        "evidence_available": ratio == 1,
        "blocking_reasons": [] if ratio == 1 else ["artifact_completeness_gap"],
        "warnings": [],
    }

