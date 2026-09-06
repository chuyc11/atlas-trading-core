"""Boundary check for evidence-backed reevaluation prep."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import BOUNDARY, DEFAULT_AS_OF_DATE, FORBIDDEN_ARTIFACT_NAMES, FORBIDDEN_POSITIVE_WORDING, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_prep_boundary_check(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, source_gate_decision: str = "blocked", blocking_reasons: list[str] | None = None, warnings: list[str] | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    forbidden_wording = _forbidden_wording_hits(paths, as_of_date)
    blocking = list(blocking_reasons or [])
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if forbidden_wording:
        blocking.append("forbidden_positive_wording_present")
    return {
        "boundary_id": "A-SHARE-EVIDENCE-BACKED-PREP-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_gate_decision,
        **BOUNDARY,
        "forbidden_artifacts_present": forbidden_artifacts,
        "forbidden_wording_positive_hits": forbidden_wording,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": list(warnings or []),
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    roots = [
        paths.data_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date,
        paths.outputs_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date,
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]
    found = []
    for root in roots:
        if root.exists():
            for path in root.rglob("*"):
                if path.name in FORBIDDEN_ARTIFACT_NAMES:
                    found.append(str(path))
    return found


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[dict[str, Any]]:
    root = paths.outputs_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date
    hits: list[dict[str, Any]] = []
    if not root.exists():
        return hits
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase in text:
                hits.append({"path": str(Path(path)), "phrase": phrase})
    return hits

