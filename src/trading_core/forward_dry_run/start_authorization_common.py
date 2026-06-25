"""Shared helpers for v0.6.2 forward dry-run start authorization artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.execution.common import read_dict, rel
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


RELEASE_CANDIDATE = "v0.6.2-forward-dry-run-start-authorization-pack-audited"
BASELINE_FROM = "v0.6.1-daily-workflow-binding-audited"
NEXT_REQUIRED_ACTION = "owner_manual_confirmation"
AUTHORIZATION_NOTICE = "v0.6.2 creates an authorization pack only and does not start forward dry-run"
AS_OF_DATE = "2024-12-31"
REQUIRED_PHRASE = "I explicitly authorize starting forward dry-run day 1"


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def authorization_boundary(scope_key: str) -> dict[str, Any]:
    return {
        scope_key: True,
        "run_daily_called": False,
        "forward_dry_run_started": False,
        "forward_dry_run_validated": False,
        "main_ledger_written": False,
        "manual_confirmation_complete": False,
        "forward_dry_run_start_authorized": False,
        "day1_start_allowed": False,
        "day1_prompt_generated": False,
        "labels_used_as_authorization": False,
        "ml_shadow_used_as_authorization": False,
        "experiments_used_as_authorization": False,
        "llm_trading_decision": False,
        "rl_used": False,
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
        "live_trading_ready": False,
        "broker_connected": False,
        "ml_trading_approved": False,
        "llm_trading_approved": False,
        "rl_trading_approved": False,
    }


def non_claim_markdown() -> list[str]:
    return [
        f"- {AUTHORIZATION_NOTICE}",
        "- run-daily not called",
        "- forward dry-run not started",
        "- forward dry-run not validated",
        "- main ledger not written",
        "- manual confirmation defaults false",
        "- owner authorization defaults false",
        "- not forward dry-run validation",
        "- not strategy effectiveness proof",
        "- not live trading readiness",
        "- no broker connected",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
    ]


def write_artifact(json_path: Path, payload: dict[str, Any], report_path: Path, markdown: str) -> dict[str, Any]:
    write_json_markdown(json_path, payload, report_path, markdown)
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def system_json(paths: ProjectPaths, filename: str) -> Path:
    return paths.data_dir / "system" / filename


def system_report(paths: ProjectPaths, filename: str) -> Path:
    return paths.outputs_dir / "system" / filename


def audit_report(paths: ProjectPaths, filename: str) -> Path:
    return paths.outputs_dir / "audit" / filename


def read_system(paths: ProjectPaths, filename: str) -> dict[str, Any]:
    return read_dict(system_json(paths, filename))


def artifact_record(paths: ProjectPaths, filename: str, *, status: str | None = None) -> dict[str, Any]:
    path = system_json(paths, filename)
    record: dict[str, Any] = {"path": rel(path, paths), "exists": path.exists()}
    if status is not None:
        record["status"] = status
    return record


def passed_without_blockers(payload: dict[str, Any]) -> bool:
    return payload.get("overall_passed") is True and not payload.get("blocking_reasons")


def manual_confirmation_complete(payload: dict[str, Any]) -> bool:
    return payload.get("manual_confirmation_complete") is True


def start_authorized(payload: dict[str, Any]) -> bool:
    return payload.get("forward_dry_run_start_authorized") is True


def command_preview_payload() -> dict[str, Any]:
    return {
        "preview_id": "FORWARD-DRY-RUN-RUN-DAILY-COMMAND-PREVIEW",
        "command": "python -m trading_core.cli run-daily --mode forward-dry-run --day-index 1",
        "preview_only": True,
        "executed": False,
        "run_daily_called": False,
        "requires_start_gate_allowed": True,
        "requires_owner_confirmation": True,
        "boundary": {
            "command_preview_only": True,
            "forward_dry_run_started": False,
            "main_ledger_written": False,
        },
    }

