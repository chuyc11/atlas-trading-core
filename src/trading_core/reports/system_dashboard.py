"""Trading Core system dashboard for v0.5."""

from __future__ import annotations

from typing import Any

from trading_core.reports.research_common import default_paths, file_exists, utc_now_id, write_json_and_markdown
from trading_core.storage.file_paths import ProjectPaths


def build_system_dashboard(
    include_artifact_inventory: bool = False,
    include_release_status: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    dashboard_id, created_at = utc_now_id("SYSDASH")
    version_path = paths.project_root / "VERSION"
    current_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
    inventory = {
        "real_data_validation": file_exists(paths.outputs_dir / "validation", "real_data_validation_summary.json") or file_exists(paths.outputs_dir, "validation/*.json"),
        "historical_replay": file_exists(paths.data_dir / "replays", "*.json") or file_exists(paths.outputs_dir / "replays", "*.md"),
        "ml_shadow_report": file_exists(paths.data_dir / "shadow", "ml_shadow_research_summary-*.json"),
        "experiment_system_audit": (paths.data_dir / "experiments" / "experiment_system_audit.json").exists(),
        "weekly_report": file_exists(paths.data_dir / "reports", "weekly_research_summary-*.json"),
        "monthly_report": file_exists(paths.data_dir / "reports", "monthly_research_summary-*.json"),
    }
    payload = {
        "dashboard_id": dashboard_id,
        "created_at": created_at,
        "current_version": current_version,
        "release_status": {
            "v0.1": "completed",
            "v0.2": "historical-real-data validated",
            "v0.3": "ml-shadow-pipeline audited",
            "v0.4": "strategy-experiment-system audited",
            "v0.5": "in_progress",
        } if include_release_status else {},
        "artifact_inventory": inventory if include_artifact_inventory else inventory,
        "known_limitations": [
            "forward 30d dry-run not completed",
            "full global-briefing historical replay not completed",
            "strategy effectiveness not proven",
            "no live trading",
        ],
        "warnings": [],
        "safety_boundary": {
            "broker_connected": False,
            "live_trading": False,
            "rl_enabled": False,
            "llm_trading_decision": False,
            "write_main_ledger": False,
        },
    }
    json_path = paths.data_dir / "system" / "system_dashboard.json"
    md_path = paths.outputs_dir / "system" / "SYSTEM_DASHBOARD.md"
    write_json_and_markdown(json_path, payload, md_path, build_system_dashboard_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_system_dashboard_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Trading Core System Dashboard",
        "",
        "## 1. Version Status",
        f"- current VERSION: {payload['current_version']}",
        "- latest known tag: v0.4.0-strategy-experiment-system-audited",
        f"- release stages: {payload.get('release_status', {})}",
        "",
        "## 2. Completed Milestones",
        "- v0.1 core hardened",
        "- v0.2 historical real-data validated",
        "- v0.2.1 price-only historical replay validated",
        "- v0.3 ML shadow pipeline audited",
        "- v0.4 strategy experiment system audited",
        "",
        "## 3. Artifact Inventory",
        "| artifact | exists | notes |",
        "|---|---|---|",
    ]
    for name, exists in payload["artifact_inventory"].items():
        lines.append(f"| {name} | {str(exists).lower()} | {'present' if exists else 'missing'} |")
    lines.extend(
        [
            "",
            "## 4. Current Research Status",
            "- trading core: file-backed virtual trading research",
            "- ML shadow: shadow only, not active",
            "- experiments: research artifacts only",
            "- reports: v0.5 in progress",
            "- validations: historical and audit evidence only",
            "",
            "## 5. Known Limitations",
            "- forward 30d dry-run not completed",
            "- full global-briefing replay not completed",
            "- no real broker",
            "- no live trading",
            "- strategy effectiveness not proven",
            "",
            "## 6. Safety Boundary",
            "- no broker",
            "- no live trading",
            "- no RL active trading",
            "- no LLM trading decision",
            "- no active promotion",
            "",
        ]
    )
    return "\n".join(lines)
