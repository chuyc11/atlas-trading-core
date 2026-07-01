"""v0.9.0 full regression plan."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_v090_full_regression_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "plan_id": "A-SHARE-V090-FULL-REGRESSION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "full_pytest_command": "python -m pytest",
        "full_pytest_run": False,
        "full_pytest_required_in_v090": True,
        "audit_sweep_commands": [
            "python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-quality-exceptions --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-readiness-recovery --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-readiness-recovery-execution --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-controlled-gate-reevaluation --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-recovery-evidence --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-evidence-backed-reevaluation-prep --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-v0820-gate-outcome --as-of-date 2026-06-26",
            "python -m trading_core.cli audit-a-share-owner-closeout-review --as-of-date 2026-06-26",
        ],
        "boundary_scan_commands": [
            "rg \"BROKER_ORDER|REAL_ORDER|ORDER_PREVIEW|BUY_LIST|SELL_LIST\" data outputs",
            "rg \"run-daily|easytrader|THSTrader\" src tests docs",
        ],
        "forbidden_artifact_scan": "scan data/orders data/trades data/accounts outputs/orders outputs/trades outputs/accounts and v0.8.21 output dirs",
        "forbidden_wording_scan": "scan owner-facing markdown for positive trading wording outside negative disclaimer context",
        "source_trace_consistency_checks": ["verify source trace completeness", "verify SHA256 hashes where available"],
        "docs_freeze_checks": ["README", "RELEASE_NOTES", "CLI_REFERENCE", "COMMAND_COOKBOOK", "ARTIFACT_MAP", "TESTING_POLICY"],
    }
