"""Create a completed manual confirmation checklist v2 for v0.6.2.1."""

from __future__ import annotations

import re
from typing import Any

from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import CONFIRMATION_ITEMS
from trading_core.forward_dry_run.start_authorization_common import MATERIALIZATION_NOTICE, materialization_non_claim_markdown, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def complete_forward_dry_run_manual_confirmation_checklist_v2(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "checklist_id": "FORWARD-DRY-RUN-MANUAL-CONFIRMATION-CHECKLIST-V2-COMPLETED",
        "source_checklist": "data/system/forward_dry_run_manual_confirmation_checklist_v2.json",
        "manual_confirmation_complete": True,
        "confirmation_scope": "start_authorization_preparation",
        "day1_execution_authorized": False,
        "items": [{"item_id": _item_id(item), "item": item, "confirmed": True} for item in CONFIRMATION_ITEMS],
        "boundary": {
            "manual_confirmation_only": True,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_manual_confirmation_checklist_v2_completed.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_MANUAL_CONFIRMATION_CHECKLIST_V2_COMPLETED.md"),
        build_markdown(payload),
    )


def _item_id(item: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", item.lower()).strip("_")
    return base.replace("i_", "", 1)[:80]


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Manual Confirmation Checklist V2 Completed",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Summary",
        "- manual_confirmation_complete: true",
        "- confirmation_scope: start_authorization_preparation",
        "- day1_execution_authorized: false",
        "",
        "## Items",
    ]
    lines.extend(f"- [x] {item['item_id']}" for item in payload["items"])
    lines.extend(["", "## Boundary", *materialization_non_claim_markdown(), ""])
    return "\n".join(lines)

