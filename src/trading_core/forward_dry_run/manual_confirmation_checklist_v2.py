"""Build owner-facing manual confirmation checklist v2."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import AUTHORIZATION_NOTICE, authorization_boundary, non_claim_markdown, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id


CONFIRMATION_ITEMS = [
    "I have reviewed the project boundary.",
    "I understand this is virtual-only forward dry-run, not real trading.",
    "I understand no broker is connected.",
    "I understand no real orders will be placed.",
    "I reviewed v0.5.9 execution rules.",
    "I reviewed v0.6.0 baseline strategy pack.",
    "I reviewed v0.6.1 daily workflow binding.",
    "I reviewed protected path residue scan.",
    "I reviewed current daily workflow readiness snapshot.",
    "I accept known warnings/nits.",
    "I authorize preparing, but not executing, day1 run-daily preview.",
    "I understand day1 requires a separate explicit owner confirmation.",
]


def build_forward_dry_run_manual_confirmation_checklist_v2(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    checklist_id, created_at = timestamp_id("FORWARD-DRY-RUN-MANUAL-CONFIRMATION-CHECKLIST-V2")
    payload: dict[str, Any] = {
        "checklist_id": checklist_id,
        "created_at": created_at,
        "confirmation_items": [{"item": item, "confirmed": False} for item in CONFIRMATION_ITEMS],
        "manual_confirmation_complete": False,
        "does_not_auto_complete": True,
        "boundary": authorization_boundary("manual_confirmation_checklist_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_manual_confirmation_checklist_v2.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_MANUAL_CONFIRMATION_CHECKLIST_V2.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Forward Dry-Run Manual Confirmation Checklist V2", "", AUTHORIZATION_NOTICE, "", "## Confirmation Items"]
    lines.extend(f"- [ ] {item['item']}" for item in payload["confirmation_items"])
    lines.extend(["", "## Defaults", "- manual_confirmation_complete=false", "- all confirmation values default false", "", "## Boundary", *non_claim_markdown(), ""])
    return "\n".join(lines)

