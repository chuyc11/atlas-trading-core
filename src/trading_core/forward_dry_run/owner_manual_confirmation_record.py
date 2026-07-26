"""Materialize owner manual confirmation for v0.6.2.1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import (
    MATERIALIZATION_NOTICE,
    materialization_non_claim_markdown,
    paths_or_default,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


def build_owner_manual_confirmation_record(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "record_id": "FORWARD-DRY-RUN-OWNER-MANUAL-CONFIRMATION-RECORD",
        "owner_confirmation_recorded": True,
        "owner_authorized_next_step": True,
        "owner_authorized_day1_execution": False,
        "confirmation_scope": "authorization_materialization_only",
        "day1_execution_requires_separate_prompt": True,
        "boundary": {
            "confirmation_record_only": True,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_owner_manual_confirmation_record.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_OWNER_MANUAL_CONFIRMATION_RECORD.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Owner Manual Confirmation Record",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Confirmation",
        "- owner_confirmation_recorded: true",
        "- owner_authorized_next_step: true",
        "- owner_authorized_day1_execution: false",
        "- day1_execution_requires_separate_prompt: true",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

