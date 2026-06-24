"""Latest artifact locator."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import relative, write_json_markdown


SUPPORTED_TYPES = {"report", "audit", "experiment", "ml-shadow", "handoff", "dashboard", "all"}


def locate_latest_artifact(
    query_type: str,
    open_command: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    if query_type not in SUPPORTED_TYPES:
        raise ValueError(f"unsupported artifact type: {query_type}")
    warnings: list[str] = []
    if query_type == "all":
        latest_by_type = {
            item: _latest_record(_candidates(item, paths), paths, warnings, item)
            for item in sorted(SUPPORTED_TYPES - {"all"})
        }
        latest = None
        candidates = []
    else:
        candidates = _candidates(query_type, paths)
        latest = _latest_record(candidates, paths, warnings, query_type)
        latest_by_type = {}
    payload = {
        "query_type": query_type,
        "latest": latest,
        "latest_by_type": latest_by_type,
        "candidates": [_record(path, paths, query_type) for path in candidates],
        "warnings": warnings,
        "open_command": _open_command(latest["path"] if latest else None) if open_command else None,
        "boundary": {
            "locator_only": True,
            "opened_file": False,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "latest_artifact.json"
    report_path = paths.outputs_dir / "system" / "LATEST_ARTIFACT.md"
    write_json_markdown(json_path, payload, report_path, build_latest_artifact_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_latest_artifact_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Latest Artifact", "", f"- query_type: {payload['query_type']}"]
    if payload["latest"]:
        lines.append(f"- latest: {payload['latest']['path']}")
    if payload["latest_by_type"]:
        lines.extend(["", "## Latest by Type"])
        for key, value in payload["latest_by_type"].items():
            lines.append(f"- {key}: {value['path'] if value else 'none'}")
    if payload.get("open_command"):
        lines.append(f"- open_command: `{payload['open_command']}`")
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {warning}" for warning in payload["warnings"]] or ["- none"])
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- locator only",
            "- no file was opened",
            "- no run-daily",
            "- no orders/trades/portfolio/accounts written",
            "- This system is not live-ready.",
            "- Forward 30d dry-run is not completed.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidates(query_type: str, paths: ProjectPaths) -> list[Path]:
    patterns = {
        "report": ["outputs/reports/*.md"],
        "audit": ["outputs/audit/*.md"],
        "experiment": ["data/experiments/*.json", "outputs/experiments/*.md"],
        "ml-shadow": ["data/shadow/*", "outputs/shadow/*.md"],
        "handoff": ["outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md", "data/system/final_handoff_review_summary.json"],
        "dashboard": ["outputs/system/SYSTEM_DASHBOARD.md", "data/system/system_dashboard.json", "outputs/experiments/EXPERIMENT_DASHBOARD.md", "data/experiments/experiment_dashboard.json"],
    }
    files: list[Path] = []
    for pattern in patterns[query_type]:
        files.extend(path for path in paths.project_root.glob(pattern) if path.is_file())
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def _latest_record(candidates: list[Path], paths: ProjectPaths, warnings: list[str], query_type: str) -> dict[str, Any] | None:
    if not candidates:
        warnings.append(f"no candidates found for type={query_type}")
        return None
    return _record(candidates[0], paths, query_type)


def _record(path: Path, paths: ProjectPaths, category: str) -> dict[str, Any]:
    modified = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
    return {
        "path": relative(path, paths.project_root),
        "modified_at": modified,
        "exists": path.exists(),
        "category": category,
    }


def _open_command(path: str | None) -> str | None:
    if not path:
        return None
    return f"start {path}"
