"""v0.5.1 validation gap remediation artifact."""

from __future__ import annotations

import json
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


def write_v051_validation_gap_remediation(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    payload: dict[str, Any] = {
        "remediation_id": "V051-GAP-REMEDIATION",
        "base_version": "v0.5.0-research-reporting-control-plane-audited",
        "base_audit_commit": "e61c4a9",
        "remediated_gaps": [
            {
                "gap_id": "GAP-002",
                "status": "remediated",
                "fix": "project_timezone changed to Asia/Shanghai",
            },
            {
                "gap_id": "GAP-003",
                "status": "remediated",
                "fix": "max_daily_turnover is enforced by risk engine",
            },
            {
                "gap_id": "GAP-004",
                "status": "remediated",
                "fix": "mistake_pattern_library JSON now includes explicit diagnostic boundary metadata",
            },
        ],
        "deferred_gaps": [
            {
                "gap_id": "GAP-001",
                "status": "deferred_to_v0.6",
                "reason": "market-rule-aware execution requires larger simulation realism release",
            },
            {
                "gap_id": "GAP-005",
                "status": "deferred_to_v0.7",
                "reason": "generalized Point-in-Time schema requires separate data architecture release",
            },
        ],
        "boundary": {
            "remediation_only": True,
            "write_main_ledger": False,
            "strategy_state_changed": False,
            "strategy_parameters_changed": False,
            "promotion_triggered": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / "v051_validation_gap_remediation.json"
    report_path = paths.outputs_dir / "audit" / "V051_VALIDATION_GAP_REMEDIATION.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_v051_remediation_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_v051_remediation_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# v0.5.1 Validation Gap Remediation",
        "",
        "## Remediated Gaps",
        "- timezone",
        "- max_daily_turnover enforcement",
        "- mistake pattern boundary metadata",
        "",
        "## Deferred Gaps",
        "- market-rule-aware execution deferred to v0.6",
        "- generalized Point-in-Time schema deferred to v0.7",
        "",
        "## Safety Boundary",
        "- remediation only",
        "- no strategy state changed",
        "- no strategy parameter changed",
        "- no promotion triggered",
        "- no orders/trades/portfolio/accounts written",
        "- run-daily not called",
        "",
        "## Details",
    ]
    lines.extend(f"- {gap['gap_id']}: {gap['fix']}" for gap in payload["remediated_gaps"])
    lines.extend(["", "## Deferred Details"])
    lines.extend(f"- {gap['gap_id']}: {gap['reason']}" for gap in payload["deferred_gaps"])
    lines.append("")
    return "\n".join(lines)
