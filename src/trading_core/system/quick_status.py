"""Quick status summary for project re-entry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import relative
from trading_core.system.common import write_json_markdown


PYTEST_BASELINE = "381 passed, 1 skipped"


def build_quick_status(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    current_version = _read_text(paths.project_root / "VERSION").strip() or "unknown"
    latest_handoff = _safe_latest("handoff", paths)
    latest_dashboard = _safe_latest("dashboard", paths)
    latest_audit = _safe_latest("audit", paths)
    payload = {
        "current_version": current_version,
        "latest_handoff_report": latest_handoff,
        "latest_system_dashboard": latest_dashboard,
        "latest_audit": latest_audit,
        "pytest_baseline": PYTEST_BASELINE,
        "known_limitations": [
            "forward 30d dry-run not completed",
            "not live trading ready",
            "strategy effectiveness not proven",
        ],
        "recommended_next_command": "python -m trading_core.cli report-index",
        "boundary": {
            "status_only": True,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "quick_status.json"
    report_path = paths.outputs_dir / "system" / "QUICK_STATUS.md"
    write_json_markdown(json_path, payload, report_path, build_quick_status_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_quick_status_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Quick Status",
        "",
        f"- current_version: {payload['current_version']}",
        f"- latest_handoff_report: {payload['latest_handoff_report']}",
        f"- latest_system_dashboard: {payload['latest_system_dashboard']}",
        f"- latest_audit: {payload['latest_audit']}",
        f"- pytest_baseline: {payload['pytest_baseline']}",
        f"- recommended_next_command: `{payload['recommended_next_command']}`",
        "",
        "## Known Limitations",
    ]
    lines.extend(f"- {item}" for item in payload["known_limitations"])
    lines.extend(
        [
            "",
            "## Boundary",
            "- status only",
            "- no run-daily",
            "- no orders/trades/portfolio/accounts written",
            "- This system is not live-ready.",
            "- Forward 30d dry-run is not completed.",
            "",
        ]
    )
    return "\n".join(lines)


def _safe_latest(query_type: str, paths: ProjectPaths) -> str | None:
    patterns = {
        "handoff": ["outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md"],
        "dashboard": ["outputs/system/SYSTEM_DASHBOARD.md", "data/system/system_dashboard.json"],
        "audit": ["outputs/audit/*.md"],
    }
    candidates: list[Path] = []
    for pattern in patterns[query_type]:
        candidates.extend(path for path in paths.project_root.glob(pattern) if path.is_file())
    if not candidates:
        return None
    latest = sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[0]
    return relative(latest, paths.project_root)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""
