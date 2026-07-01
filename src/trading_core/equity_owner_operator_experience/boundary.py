"""Boundary check for owner/operator experience."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import (
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    SOURCE_RELEASE_CANDIDATE,
    SOURCE_WORKFLOW_MODE,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_operator_boundary_check(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    roots = [
        paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date,
        paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date,
    ]
    forbidden_artifacts = []
    wording_hits = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.name in FORBIDDEN_ARTIFACT_NAMES:
                forbidden_artifacts.append(str(path))
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for phrase in FORBIDDEN_POSITIVE_WORDING:
                    if phrase in text:
                        wording_hits.append(f"{path}:{phrase}")
    blocking = []
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if wording_hits:
        blocking.append("forbidden_positive_wording_present")
    return {
        "boundary_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "operator_experience_only": True,
        "known_blocked_state_hardening_only": True,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "rerun_owner_readiness_gate": False,
        "rerun_build_from_existing_data": False,
        "rerun_daily_pack": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "run_full_pytest": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "public_network_refresh_run": False,
        "full_research_run": False,
        "old_run_daily_called": False,
        "run_daily_called": False,
        "day2_executed": False,
        "external_notifications_sent": False,
        "execute_remediation_actions": False,
        "research_only": True,
        "virtual_only": True,
        "real_portfolio_generated": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        "live_trading_ready": False,
        "real_account_data_read": False,
        "operator_experience_used_as_trade_instruction": False,
        "protected_path_modifications_detected": False,
        "forbidden_artifacts_present": forbidden_artifacts,
        "forbidden_wording_positive_hits": wording_hits,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }
