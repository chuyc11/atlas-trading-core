"""Shared helpers for v0.5.8.1 plan alignment artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths


RELEASE_CANDIDATE = "v0.5.8.1-plan-alignment-and-mvp-gap-audited"
PLAN_ALIGNMENT_NOTICE = "Plan alignment is an audit, not day 1 authorization."

VALID_EVIDENCE_TYPES = {"module", "cli", "test", "artifact", "doc", "release_tag", "audit", "report"}
VALID_GAP_STATUSES = {"passed", "partial", "missing", "deferred", "not_applicable"}


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def read_dict(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def rel(path: str | Path | None, paths: ProjectPaths) -> str | None:
    if not path:
        return None
    candidate = Path(path)
    try:
        return candidate.relative_to(paths.project_root).as_posix()
    except ValueError:
        return str(candidate)


def resolve_path(raw: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not raw:
        return default
    path = Path(raw)
    return path if path.is_absolute() else paths.project_root / path


def standard_boundary(scope_key: str) -> dict[str, Any]:
    return {
        scope_key: True,
        "run_daily_called": False,
        "forward_dry_run_started": False,
        "forward_dry_run_validated": False,
        "main_ledger_written": False,
        "labels_used_as_authorization": False,
        "ml_shadow_used_as_authorization": False,
        "experiments_used_as_authorization": False,
        "llm_trading_decision": False,
        "rl_used": False,
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
        "live_trading_ready": False,
        "broker_connected": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def contains_text(path: Path, tokens: list[str]) -> bool:
    if not path.exists() or path.is_dir():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    return any(token.lower() in text for token in tokens)

