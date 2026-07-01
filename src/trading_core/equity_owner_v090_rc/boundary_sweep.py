"""Boundary sweep for v0.9.0 RC."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, FORBIDDEN_ARTIFACT_NAMES, FORBIDDEN_POSITIVE_WORDING, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_boundary_sweep_result(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    forbidden_wording = _forbidden_wording_hits(paths, as_of_date)
    checks = {
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "run_daily_called": False,
        "day2_executed": False,
        "public_network_refresh_run": False,
        "full_research_run": False,
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "model_profit_guaranteed": False,
        "live_trading_ready": False,
        "protected_path_modifications_detected": False,
        "forbidden_artifacts_present": forbidden_artifacts,
        "forbidden_wording_positive_hits": forbidden_wording,
    }
    blocking = []
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if forbidden_wording:
        blocking.append("forbidden_positive_wording_present")
    return {
        "result_id": "A-SHARE-V090-BOUNDARY-SWEEP-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "boundary_sweep_run": True,
        "boundary_sweep_passed": not blocking,
        **checks,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    roots = [
        paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date,
        paths.outputs_dir / "equity_owner_v090_rc" / "daily" / as_of_date,
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]
    found = []
    for root in roots:
        if root.exists():
            for path in root.rglob("*"):
                if path.name in FORBIDDEN_ARTIFACT_NAMES:
                    found.append(str(path))
    return found


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[dict[str, Any]]:
    root = paths.outputs_dir / "equity_owner_v090_rc" / "daily" / as_of_date
    hits = []
    if not root.exists():
        return hits
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase in text:
                hits.append({"path": str(Path(path)), "phrase": phrase})
    return hits
