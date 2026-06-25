"""Generate run-daily command preview metadata without executing run-daily."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import AUTHORIZATION_NOTICE, command_preview_payload, non_claim_markdown, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_forward_dry_run_run_daily_command_preview(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = command_preview_payload()
    return write_artifact(
        system_json(paths, "forward_dry_run_run_daily_command_preview.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_RUN_DAILY_COMMAND_PREVIEW.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Run-Daily Command Preview",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Preview",
        f"- command: `{payload['command']}`",
        "- preview_only: true",
        "- executed: false",
        "- run_daily_called: false",
        "- metadata only; not instructions to execute day1",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

