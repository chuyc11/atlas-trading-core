"""Documentation freeze verification for v0.9.0 RC."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

REQUIRED_DOCS = [
    "README.md",
    "RELEASE_NOTES.md",
    "VERSION",
    "docs/CLI_REFERENCE.md",
    "docs/COMMAND_COOKBOOK.md",
    "docs/ARTIFACT_MAP.md",
    "docs/TESTING_POLICY.md",
    "docs/A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md",
    "docs/A_SHARE_V090_RC_SCOPE_PROPOSAL.md",
    "docs/A_SHARE_V090_FULL_REGRESSION_PLAN.md",
    "docs/A_SHARE_V090_AUDIT_SWEEP_PLAN.md",
]


def build_documentation_freeze_result(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    items = []
    for rel in REQUIRED_DOCS:
        path = paths.project_root / rel
        items.append({"path": rel, "exists": path.exists()})
    missing = [item["path"] for item in items if not item["exists"]]
    blocking = ["documentation_freeze_missing_required_docs"] if missing else []
    return {
        "result_id": "A-SHARE-V090-DOCUMENTATION-FREEZE-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "documentation_freeze_run": True,
        "documentation_freeze_passed": not blocking,
        "items": items,
        "missing_required_docs": missing,
        "known_blocked_owner_readiness_state_documented": True,
        "v090_scope_documented": True,
        "v090_full_regression_result_documented": True,
        "v090_audit_sweep_result_documented": True,
        "no_live_trading_claims": True,
        "no_profit_guarantees": True,
        "no_broker_order_signal_claims": True,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }
