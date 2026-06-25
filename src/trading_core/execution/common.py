"""Shared helpers for v0.5.9 A-share execution hardening."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_jsonl
from trading_core.system.common import default_paths


RELEASE_CANDIDATE = "v0.5.9-ashare-execution-rules-hardened"
HARDENING_NOTICE = "v0.5.9 hardens virtual execution rules but does not start forward dry-run."
MARKETS = ["SSE", "SZSE", "HKEX"]


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def read_dict(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    return [row for row in rows if isinstance(row, dict)]


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(path, rows)


def resolve_path(raw: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not raw:
        return default
    path = Path(raw)
    return path if path.is_absolute() else paths.project_root / path


def rel(path: str | Path | None, paths: ProjectPaths) -> str | None:
    if not path:
        return None
    candidate = Path(path)
    try:
        return candidate.relative_to(paths.project_root).as_posix()
    except ValueError:
        return str(candidate)


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


def boundary_markdown(scope: str) -> list[str]:
    return [
        f"- {scope}",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- not strategy effectiveness proof",
        "- not live trading readiness",
    ]

