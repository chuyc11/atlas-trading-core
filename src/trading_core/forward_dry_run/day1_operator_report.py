"""Human-readable operator report for virtual forward dry-run day 1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, day_json, day_report, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_risk_and_boundary_report import build_day1_risk_and_boundary_report
from trading_core.storage.file_paths import ProjectPaths


def build_day1_operator_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    risk_path = day_json(paths, "day1_risk_and_boundary_report.json")
    if not risk_path.exists():
        build_day1_risk_and_boundary_report(paths=paths)
    snapshot = read_json_file(day_json(paths, "day1_input_snapshot.json"))
    signals = read_json_file(day_json(paths, "day1_strategy_signals.json"))
    orders = read_json_file(day_json(paths, "day1_virtual_order_preview.json"))
    execution = read_json_file(day_json(paths, "day1_virtual_execution_result.json"))
    ledger = read_json_file(day_json(paths, "day1_forward_dry_run_ledger_snapshot.json"))
    risk = read_json_file(risk_path)
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-OPERATOR-REPORT",
        "day_index": DAY_INDEX,
        "as_of_date": snapshot.get("as_of_date"),
        "execution_date": signals.get("signals", [{}])[0].get("execution_earliest_date"),
        "strategies_included": [signal.get("strategy_id") for signal in signals.get("signals", [])],
        "signals_summary": {"strategies_total": signals.get("strategies_total"), "strategies_generated": signals.get("strategies_generated")},
        "virtual_orders_summary": orders.get("summary", {}),
        "virtual_fills_summary": {"fills_count": len(execution.get("fills", []))},
        "virtual_rejects_summary": {"rejects_count": len(execution.get("rejects", []))},
        "virtual_cash_summary": ledger.get("virtual_cash", {}),
        "virtual_positions_summary": ledger.get("virtual_positions", {}),
        "virtual_valuation_summary": ledger.get("virtual_valuation", {}),
        "warnings": risk.get("warnings", []),
        "operator_checklist_for_day2": [
            "Review day1 fills and rejects.",
            "Review cash and position invariants.",
            "Review risk and boundary report.",
            "Confirm no main ledger artifacts were written.",
        ],
        "next_allowed_action": "forward_dry_run_day2_continuation_after_operator_review",
        "explicit_non_claims": non_claim_lines(),
    }
    return write_artifact(day_json(paths, "day1_operator_report.json"), payload, day_report(paths, "DAY1_OPERATOR_REPORT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Operator Report",
        "",
        f"- day_index: {payload['day_index']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- execution_date: {payload['execution_date']}",
        f"- strategies_included: {', '.join(payload['strategies_included'])}",
        f"- orders_total: {payload['virtual_orders_summary'].get('orders_total')}",
        f"- fills_count: {payload['virtual_fills_summary'].get('fills_count')}",
        f"- rejects_count: {payload['virtual_rejects_summary'].get('rejects_count')}",
        "",
        "## Operator Checklist For Day 2",
    ]
    lines.extend(f"- {item}" for item in payload["operator_checklist_for_day2"])
    lines.extend(["", "## Explicit Non-Claims", *payload["explicit_non_claims"], ""])
    return "\n".join(lines)

