"""Recovery task evidence registry."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_readiness_recovery_execution.execution_config import ALLOWED_EVIDENCE_TYPES, DEFAULT_AS_OF_DATE, FORBIDDEN_EVIDENCE_TYPES, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_recovery_task_evidence_registry(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, backlog: dict[str, Any]) -> dict[str, Any]:
    paths = default_paths(paths)
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    records = []
    evidence_root = paths.data_dir / "equity_owner_readiness_recovery_execution" / "evidence" / as_of_date
    for task in backlog.get("tasks", []):
        evidence_path = evidence_root / f"{task['task_id']}_completion_evidence.json"
        available = evidence_path.exists()
        records.append(
            {
                "evidence_id": f"EVIDENCE:{task['task_id']}:completion",
                "target_version": TARGET_VERSION,
                "as_of_date": as_of_date,
                "source_task_id": task["task_id"],
                "evidence_type": "artifact_exists",
                "evidence_artifact_path": str(evidence_path),
                "evidence_sha256": sha256_file(evidence_path) if available else "",
                "evidence_available": available,
                "evidence_confidence": "high" if available else "none",
                "evidence_summary": "completion evidence artifact exists" if available else "no local completion evidence artifact found",
                "supports_task_status": "evidence_available" if available else "planned",
                "created_at": generated_at,
            }
        )
    forbidden = sorted({row["evidence_type"] for row in records if row["evidence_type"] in FORBIDDEN_EVIDENCE_TYPES})
    return {
        "registry_id": "A-SHARE-RECOVERY-TASK-EVIDENCE-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allowed_evidence_types": sorted(ALLOWED_EVIDENCE_TYPES),
        "forbidden_evidence_types": sorted(FORBIDDEN_EVIDENCE_TYPES),
        "evidence_record_count": len(records),
        "evidence_available_count": sum(1 for row in records if row["evidence_available"]),
        "forbidden_evidence_types_detected": forbidden,
        "task_existence_alone_is_completion_evidence": False,
        "records": records,
    }


def evidence_paths_exist(registry: dict[str, Any]) -> bool:
    for row in registry.get("records", []):
        if row.get("evidence_available") and not Path(row.get("evidence_artifact_path", "")).exists():
            return False
    return True
