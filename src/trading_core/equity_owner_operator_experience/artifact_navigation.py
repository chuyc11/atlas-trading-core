"""Artifact navigation index."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_artifact_navigation_index(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    paths = default_paths(paths)
    rows = [
        _item("current_status", "Owner daily status", paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date / "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md", "report", "Start here for the current operator state.", 1),
        _item("v0.9.0_rc", "v0.9.0 RC report", paths.outputs_dir / "equity_owner_v090_rc" / "daily" / as_of_date / "A_SHARE_V090_RC_REPORT.md", "report", "Shows RC decision and full regression evidence.", 2),
        _item("known_blocked_state", "Known blocked guide", paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date / "A_SHARE_KNOWN_BLOCKED_STATE_GUIDE.md", "report", "Explains why blocked is expected.", 3),
        _item("full_regression", "Full regression result", paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date / "v090_full_pytest_result.json", "json", "Records v0.9.0 full pytest evidence.", 4),
        _item("audit_sweep", "Audit sweep result", paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date / "v090_audit_sweep_result.json", "json", "Records v0.8.13-v0.8.21 audit sweep.", 5),
        _item("closeout_review", "v0.8.21 closeout review", paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date / "closeout_summary.json", "json", "Closeout context before RC.", 6),
        _item("final_blocked_closeout", "v0.8.20 final blocked closeout", paths.data_dir / "equity_data_quality" / "a_share_owner_v0820_gate_outcome_audit.json", "json", "Explains final blocked branch.", 7),
        _item("evidence_history", "Unresolved blocker register", paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date / "unresolved_blocker_register.json", "json", "Lists unresolved blocker history.", 8),
        _item("recovery_history", "Recovery evidence audit", paths.data_dir / "equity_data_quality" / "a_share_owner_recovery_evidence_audit.json", "json", "Evidence collection history.", 9),
        _item("gate_history", "Owner readiness gate audit", paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json", "json", "Original blocked gate result.", 10),
        _item("boundary_checks", "Operator boundary check", paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date / "operator_boundary_check.json", "json", "Confirms no trading boundary was touched.", 11),
        _item("source_traces", "Operator source trace", paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date / "operator_source_trace.json", "json", "Maps source and output artifacts.", 12),
        _item("docs", "Operator quickstart", paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date / "A_SHARE_OPERATOR_QUICKSTART.md", "report", "Short operator starting point.", 13),
    ]
    return {
        "index_id": "A-SHARE-ARTIFACT-NAVIGATION-INDEX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "navigation_groups": sorted({row["group"] for row in rows}),
        "items": rows,
        "overall_passed": len(rows) >= 13,
        "blocking_reasons": [] if len(rows) >= 13 else ["navigation_items_missing"],
        "warnings": [],
    }


def _item(group: str, title: str, path: Path, artifact_type: str, why: str, priority: int) -> dict:
    return {
        "group": group,
        "title": title,
        "path": str(path),
        "artifact_type": artifact_type,
        "why_it_matters": why,
        "owner_visible": True,
        "priority": priority,
        "exists": path.exists(),
    }
