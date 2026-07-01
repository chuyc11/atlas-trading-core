"""Audit and test status summary."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION


def build_audit_and_test_status_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, full_pytest: dict[str, Any], rc_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-AUDIT-AND-TEST-STATUS-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_release": SOURCE_RELEASE_CANDIDATE,
        "full_pytest_run_in_source_release": True,
        "full_pytest_passed_in_source_release": full_pytest.get("overall_passed") is True,
        "full_pytest_result": f"{full_pytest.get('passed_count')} passed, {full_pytest.get('skipped_count')} skipped",
        "audit_sweep_passed": rc_summary.get("v090_audit_sweep_passed") is True,
        "v091_full_pytest_run": False,
        "v091_targeted_pytest_required": True,
        "current_stage_test_policy": "targeted_pytest_only",
        "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        "overall_passed": full_pytest.get("overall_passed") is True,
        "blocking_reasons": [],
        "warnings": [],
    }
