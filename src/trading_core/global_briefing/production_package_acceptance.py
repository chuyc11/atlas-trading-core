"""Production global-briefing package acceptance criteria."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


CRITERIA_ID = "GB-PRODUCTION-ACCEPTANCE-V1"
MIN_COVERAGE = 0.80
TARGET_COVERAGE = 0.90


def build_global_briefing_production_acceptance_criteria(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    payload: dict[str, Any] = {
        "criteria_id": CRITERIA_ID,
        "required": {
            "package_type": "production_global_briefing_historical",
            "local_file_available": True,
            "network_access": False,
            "min_coverage": MIN_COVERAGE,
            "target_coverage": TARGET_COVERAGE,
            "future_signal_leakage_rows": 0,
            "pit_high_severity_issues": 0,
            "unknown_warning_count": 0,
            "required_fields": [
                "as_of_date",
                "generated_at",
                "region",
                "signals",
                "source",
                "version",
            ],
        },
        "must_pass": [
            "signal_contract_validation",
            "package_coverage_audit",
            "point_in_time_audit",
            "isolated_replay_workflow",
            "integration_audit",
            "evidence_quality_report",
        ],
        "must_not_claim": [
            "strategy_effectiveness_proven",
            "forward_dry_run_validated",
            "live_trading_ready",
            "promotion_approved",
        ],
        "boundary": {
            "criteria_only": True,
            "replay_started": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "network_access": False,
            "promotion_triggered": False,
            "forward_dry_run_started": False,
        },
    }
    markdown = build_acceptance_markdown(payload)
    json_path = paths.data_dir / "system" / "global_briefing_production_acceptance_criteria.json"
    md_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_PRODUCTION_ACCEPTANCE_CRITERIA.md"
    write_json_markdown(json_path, payload, md_path, markdown)
    docs_path = paths.project_root / "docs" / "GLOBAL_BRIEFING_PRODUCTION_ACCEPTANCE.md"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(markdown, encoding="utf-8")
    return {**payload, "json_path": str(json_path), "report_path": str(md_path), "docs_path": str(docs_path)}


def build_acceptance_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Production Package Acceptance Criteria",
            "",
            "## Scope",
            "This document defines criteria for future production historical global-briefing package acceptance.",
            "",
            "It does not accept any package by itself.",
            "",
            "## Required Minimums",
            "- min coverage >= 0.80",
            "- target coverage >= 0.90",
            "- future signal leakage rows = 0",
            "- high severity PIT issues = 0",
            "- unknown warnings = 0",
            "",
            "## Required Audits",
            *[f"- {item}" for item in payload["must_pass"]],
            "",
            "## Explicit Non-Claims",
            "- package acceptance does not prove strategy effectiveness",
            "- package acceptance does not validate forward dry-run",
            "- package acceptance does not certify live trading readiness",
            "",
            "## Boundary",
            "- criteria only",
            "- no replay started",
            "- no main ledger write",
            "- no run-daily call",
            "",
        ]
    )
