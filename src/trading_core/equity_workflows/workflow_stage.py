"""Stage records for A-share daily research workflow orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_workflows.workflow_config import WORKFLOW_BOUNDARY
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


STAGE_STATUSES = {"passed", "failed", "skipped", "blocked", "not_run"}


@dataclass
class WorkflowStageRecord:
    stage_id: str
    stage_name: str
    stage_order: int
    mode: str
    command: str
    started_at: str
    finished_at: str
    duration_seconds: float
    status: str
    input_artifacts: list[str] = field(default_factory=list)
    output_artifacts: list[str] = field(default_factory=list)
    audit_artifacts: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped_reason: str = ""
    boundary_flags: dict[str, Any] = field(default_factory=lambda: dict(WORKFLOW_BOUNDARY))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def make_stage_record(
    *,
    definition: dict[str, Any],
    mode: str,
    command: str,
    status: str,
    paths: ProjectPaths,
    started_at: str,
    finished_at: str,
    blocking_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    skipped_reason: str = "",
) -> WorkflowStageRecord:
    if status not in STAGE_STATUSES:
        raise ValueError(f"invalid stage status: {status}")
    started = _parse_time(started_at)
    finished = _parse_time(finished_at)
    return WorkflowStageRecord(
        stage_id=str(definition["stage_id"]),
        stage_name=str(definition["stage_name"]),
        stage_order=int(definition["stage_order"]),
        mode=mode,
        command=command,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=max((finished - started).total_seconds(), 0.0),
        status=status,
        input_artifacts=_rel_paths(paths, definition.get("input_artifacts", [])),
        output_artifacts=_rel_paths(paths, definition.get("output_artifacts", [])),
        audit_artifacts=_rel_paths(paths, definition.get("audit_artifacts", [])),
        blocking_reasons=blocking_reasons or [],
        warnings=warnings or [],
        skipped_reason=skipped_reason,
        boundary_flags=dict(WORKFLOW_BOUNDARY),
    )


def blocked_stage_record(
    *,
    definition: dict[str, Any],
    mode: str,
    paths: ProjectPaths,
    reason: str,
) -> WorkflowStageRecord:
    now = utc_now()
    return make_stage_record(
        definition=definition,
        mode=mode,
        command=str(definition.get("validate_command") or definition.get("build_command") or ""),
        status="blocked",
        paths=paths,
        started_at=now,
        finished_at=now,
        blocking_reasons=[reason],
        skipped_reason=reason,
    )


def _rel_paths(paths: ProjectPaths, values: list[Any]) -> list[str]:
    result = []
    for value in values:
        path = Path(value) if not isinstance(value, Path) else value
        result.append(relative(path, paths.project_root))
    return result


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)
