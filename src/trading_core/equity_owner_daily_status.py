"""Read-only owner daily status CLI rendering."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from trading_core import __version__
from trading_core.storage.file_paths import ProjectPaths, project_paths

RECOMMENDED_NEXT_VERSION = "v0.9.3-a-share-data-freshness-refresh"


def build_owner_daily_status_payload(
    *, as_of_date: str, paths: ProjectPaths | None = None, current_date: date | None = None
) -> dict[str, Any]:
    paths = paths or project_paths()
    current_date = current_date or date.today()
    op_dir = paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date
    rc_dir = paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date
    status = _load_required(op_dir / "owner_daily_status_card.json")
    actions = _load_required(op_dir / "operator_action_menu.json")
    nav = _load_required(op_dir / "artifact_navigation_index.json")
    boundary = _load_required(op_dir / "safety_boundary_status_panel.json")
    v091_audit = _load_required(paths.data_dir / "equity_data_quality" / "a_share_owner_operator_experience_audit.json")
    v090_audit = _load_required(paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json")
    full_pytest = _load_required(rc_dir / "v090_full_pytest_result.json")
    audit_sweep = _load_required(rc_dir / "v090_audit_sweep_result.json")
    source_date = status.get("as_of_date") or as_of_date
    return {
        "command": "owner-daily-status",
        "as_of_date": as_of_date,
        "system_state": status.get("system_state"),
        "known_owner_readiness_state": status.get("owner_readiness_state"),
        "owner_operationally_acceptable": status.get("owner_operationally_acceptable"),
        "readiness_score": status.get("readiness_score"),
        "minimum_owner_readiness_score": status.get("minimum_owner_readiness_score"),
        "score_gap": status.get("score_gap"),
        "v090_full_pytest_passed": bool(full_pytest.get("overall_passed") and status.get("full_pytest_passed")),
        "v090_full_pytest_result": status.get("full_pytest_result") or _pytest_summary(full_pytest),
        "v090_audit_sweep_passed": bool(audit_sweep.get("audit_sweep_passed") and v090_audit.get("overall_passed")),
        "v091_operator_audit_passed": bool(v091_audit.get("overall_passed")),
        "data_staleness": {
            "source_data_date": source_date,
            "days_since_source_data": _days_since(source_date, current_date),
            "trading_days_since_source_data": None,
            "data_refresh_executed": False,
            "data_refresh_deferred_until": RECOMMENDED_NEXT_VERSION,
        },
        "safe_actions": [item["label"] for item in actions.get("actions", []) if item.get("allowed") and item.get("owner_visible")][:8],
        "forbidden_actions": _forbidden_actions(boundary),
        "key_artifacts": _key_artifacts(nav, paths.project_root),
        "not_investment_advice": True,
        "not_order_instruction": True,
        "not_live_trading_ready": True,
        "data_refresh_executed": False,
        "public_network_refresh_run": False,
        "build_from_existing_data_run": False,
        "daily_research_workflow_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "run_daily_called": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "owner_daily_status_used_as_trade_instruction": False,
    }


def render_owner_daily_status_text(payload: dict[str, Any]) -> str:
    stale = payload["data_staleness"]
    artifacts = payload["key_artifacts"][:8]
    safe_actions = payload["safe_actions"][:8]
    forbidden = payload["forbidden_actions"]
    lines = [
        "=" * 59,
        "  trading-core owner daily status",
        f"  version: trading-core {__version__}",
        f"  data as-of date: {payload['as_of_date']}",
        "=" * 59,
        "",
        "  OWNER-READINESS: BLOCKED",
        f"     score: {payload['readiness_score']} / threshold: {payload['minimum_owner_readiness_score']} / gap: {payload['score_gap']}",
        "     state: known, audited, not a system failure",
        f"     owner_operationally_acceptable = {str(payload['owner_operationally_acceptable']).lower()}",
        "",
        "  research system RC: PASSED (v0.9.0)",
        f"     v0.9.0 full pytest passed: {payload['v090_full_pytest_result']}",
        f"     audit sweep passed: {str(payload['v090_audit_sweep_passed']).lower()}",
        "     boundary: clean",
        "",
        "  data staleness",
        f"     source data date: {stale['source_data_date']}",
        f"     days since source data: {stale['days_since_source_data']} calendar days / unknown trading days",
        f"     this version does not refresh data; data refresh is deferred to {stale['data_refresh_deferred_until']}",
        "-" * 59,
        "  safe actions",
    ]
    lines.extend(f"     - {action}" for action in safe_actions)
    lines.extend(["", "  forbidden actions"])
    lines.extend(f"     - {action}" for action in forbidden)
    lines.extend(["", "-" * 59, "  key reports"])
    lines.extend(f"     {idx}. {item['title']} -> {item['path']}" for idx, item in enumerate(artifacts, 1))
    lines.extend(
        [
            "",
            "-" * 59,
            "  disclaimer",
            "     Research-only / virtual-only.",
            "     Not investment advice, not an order instruction, not live trading ready.",
            "=" * 59,
        ]
    )
    return "\n".join(lines)


def render_owner_daily_status_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def owner_daily_status_output(*, as_of_date: str, output_format: str, paths: ProjectPaths | None = None) -> str:
    payload = build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    if output_format == "json":
        return render_owner_daily_status_json(payload)
    if output_format == "text":
        return render_owner_daily_status_text(payload)
    raise ValueError(f"unsupported owner daily status format: {output_format}")


def _load_required(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required owner daily status artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pytest_summary(payload: dict[str, Any]) -> str:
    return f"{payload.get('passed_count', 0)} passed, {payload.get('skipped_count', 0)} skipped"


def _days_since(source_date: str, current_date: date) -> int | None:
    try:
        return (current_date - date.fromisoformat(source_date)).days
    except ValueError:
        return None


def _forbidden_actions(boundary: dict[str, Any]) -> list[str]:
    return [
        "broker / real account / real orders / order preview",
        "buy/sell signals / old run-daily / official day2",
        "live trading ready claim",
    ]


def _key_artifacts(nav: dict[str, Any], project_root: Path) -> list[dict[str, str]]:
    items = sorted(
        [item for item in nav.get("items", []) if item.get("owner_visible")],
        key=lambda item: item.get("priority", 999),
    )[:8]
    result = []
    for item in items:
        path = Path(item["path"])
        try:
            display_path = path.relative_to(project_root).as_posix()
        except ValueError:
            display_path = str(path)
        result.append({"title": item["title"], "path": display_path})
    return result
