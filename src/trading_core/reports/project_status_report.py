"""Project governance status report for v0.5."""

from __future__ import annotations

from typing import Any

from trading_core.reports.research_common import default_paths, utc_now_id, write_json_and_markdown
from trading_core.storage.file_paths import ProjectPaths


COMPLETED_VERSIONS = [
    "v0.1.0-core-hardened",
    "v0.2.0-historical-real-data-validated",
    "v0.2.1-price-only-historical-replay-validated",
    "v0.3.0-ml-shadow-pipeline-audited",
    "v0.4.0-strategy-experiment-system-audited",
]


def build_project_status_report(
    include_next_steps: bool = False,
    include_risk_register: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    report_id, created_at = utc_now_id("PROJECT-STATUS")
    risk_register = [
        {
            "risk_id": "RISK-001",
            "risk": "Shadow results may be misread as live trading readiness",
            "severity": "high",
            "mitigation": "Keep reports explicitly marked as research-only",
        }
    ]
    payload = {
        "report_id": report_id,
        "created_at": created_at,
        "current_stage": "v0.5-research-reporting-control-plane",
        "completed_versions": COMPLETED_VERSIONS,
        "completed_capabilities": {
            "core_trading": ["file-backed virtual trading", "risk", "valuation"],
            "real_data_validation": ["historical validation", "price-only replay"],
            "ml_shadow": ["features", "labels", "leaderboard"],
            "experiment_system": ["registry", "sweep", "comparison", "simulation", "mistake patterns"],
            "reporting": ["v0.5 reporting in progress"],
        },
        "open_items": [
            "forward 30d dry-run",
            "full global-briefing historical replay",
            "strategy effectiveness proof",
            "v0.5 release audit",
        ],
        "risk_register": risk_register if include_risk_register else risk_register,
        "next_steps": [
            "Complete v0.5 release audit",
            "Do not start RL before reporting layer is audited",
        ] if include_next_steps else [
            "Complete v0.5 release audit",
            "Do not start RL before reporting layer is audited",
        ],
        "warnings": [],
        "boundary": {
            "research_only": True,
            "live_trading": False,
            "broker_connected": False,
            "active_promotion": False,
            "write_main_ledger": False,
        },
    }
    json_path = paths.data_dir / "system" / "project_status_summary.json"
    md_path = paths.outputs_dir / "system" / "PROJECT_STATUS_REPORT.md"
    write_json_and_markdown(json_path, payload, md_path, build_project_status_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_project_status_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Project Status Report",
        "",
        "## 1. Current Stage",
        "- v0.5 research reporting control plane",
        "",
        "## 2. Completed Versions",
    ]
    lines.extend(f"- {version}" for version in payload["completed_versions"])
    lines.extend(["", "## 3. Completed Capabilities"])
    for group, items in payload["completed_capabilities"].items():
        lines.append(f"- {group}: {', '.join(items)}")
    lines.extend(["", "## 4. Open Items"])
    lines.extend(f"- {item}" for item in payload["open_items"])
    lines.extend(["", "## 5. Risk Register"])
    for risk in payload["risk_register"]:
        lines.append(f"- {risk['risk']} | severity={risk['severity']} | mitigation={risk['mitigation']}")
    lines.extend(["", "## 6. Next Steps"])
    lines.extend(f"- {step}" for step in payload["next_steps"])
    lines.extend(
        [
            "",
            "## 7. Boundary",
            "- project is research-only",
            "- no live trading",
            "- no broker",
            "- no active promotion",
            "",
        ]
    )
    return "\n".join(lines)
