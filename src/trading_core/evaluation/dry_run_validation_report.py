"""Validation report for real global-briefing dry-run coverage."""

from __future__ import annotations

from collections import Counter
from typing import Any

from trading_core.backtest.event_backtester import date_range
from trading_core.daily_run import run_daily
from trading_core.evaluation.dry_run_auditor import audit_dry_run
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.runtime.health import load_health
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


def build_dry_run_validation_report(
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    execute_missing_runs: bool = True,
) -> dict[str, Any]:
    paths = paths or project_paths()
    days = date_range(start_date, end_date)
    run_status: list[dict[str, Any]] = []
    warnings: list[str] = []
    missing_input_days: list[str] = []

    for day in days:
        input_status = _input_status(day, paths)
        if input_status["missing"]:
            missing_input_days.append(day)
            warnings.extend(f"{day}: missing input file {path}" for path in input_status["missing"])
        status = _ensure_or_read_day(day, paths, execute_missing_runs)
        run_status.append({**status, "input_files_found": input_status["found"], "input_files_missing": input_status["missing"]})

    audit = audit_dry_run(start_date, end_date, paths)
    totals = _collect_totals(days, paths)
    health_days = [row["date"] for row in run_status if row["health"]]
    successful_days = [row["date"] for row in run_status if row["health"] and not row["health"].get("errors") and row["status"] != "failed"]
    failed_days = [row["date"] for row in run_status if row["status"] == "failed" or (row["health"] and row["health"].get("errors"))]
    portfolio_status = _portfolio_continuity(days, paths)
    shadow_status = _shadow_contamination_status(audit)
    evolution_status = _evolution_status(audit)
    duplicate_status = {
        "duplicate_order_ids": audit.get("duplicate_order_ids", []),
        "duplicate_trade_ids": audit.get("duplicate_trade_ids", []),
        "passed": not audit.get("duplicate_order_ids") and not audit.get("duplicate_trade_ids"),
    }

    release_blocking_reasons = _release_blocking_reasons(
        actual_run_days=len(health_days),
        audit=audit,
        duplicate_status=duplicate_status,
        portfolio_status=portfolio_status,
        shadow_status=shadow_status,
        evolution_status=evolution_status,
        missing_input_days=missing_input_days,
    )
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "expected_trading_days": len(days),
        "actual_run_days": len(health_days),
        "missing_input_days": sorted(set(missing_input_days)),
        "successful_days": successful_days,
        "failed_days": failed_days,
        "total_signals": totals["total_signals"],
        "total_orders": totals["total_orders"],
        "total_trades": totals["total_trades"],
        "rejected_orders": totals["rejected_orders"],
        "common_rejection_reasons": dict(totals["common_rejection_reasons"]),
        "fallback_price_counts": totals["fallback_price_counts"],
        "stale_price_counts": totals["stale_price_counts"],
        "missing_price_counts": totals["missing_price_counts"],
        "portfolio_continuity_status": portfolio_status,
        "duplicate_order_trade_status": duplicate_status,
        "shadow_contamination_status": shadow_status,
        "evolution_proposal_count": totals["evolution_proposal_count"],
        "experiment_queue_growth": totals["experiment_queue_growth"],
        "evolution_throttle_status": evolution_status,
        "audit_passed": bool(audit.get("passed")),
        "critical_errors": audit.get("critical_errors", []),
        "warnings": sorted(set([*warnings, *audit.get("warnings", [])])),
        "dry_run_30d_passed": not release_blocking_reasons,
        "release_blocking_reasons": release_blocking_reasons,
        "audit_path": audit.get("json_path"),
        "run_status": run_status,
    }
    output_dir = paths.outputs_dir / "validation"
    json_path = output_dir / f"dry_run_validation_summary-{start_date}-{end_date}.json"
    report_path = output_dir / f"DRY_RUN_VALIDATION_REPORT-{start_date}-{end_date}.md"
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    write_json(json_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    return payload


def _input_status(day: str, paths: ProjectPaths) -> dict[str, list[str]]:
    expected = [
        paths.global_briefing_data_dir / f"macro_signals-{day}.jsonl",
        paths.global_briefing_data_dir / f"china-market-snapshot-{day}.json",
    ]
    found = [str(path) for path in expected if path.exists()]
    missing = [str(path) for path in expected if not path.exists()]
    return {"found": found, "missing": missing}


def _ensure_or_read_day(day: str, paths: ProjectPaths, execute_missing_runs: bool) -> dict[str, Any]:
    health = load_health(day, paths)
    if health:
        export_trading_summary(day, paths)
        return {"date": day, "status": "read_existing", "error": None, "health": health}
    if not execute_missing_runs:
        return {"date": day, "status": "missing_run", "error": "missing health file", "health": None}
    try:
        result = run_daily(day, paths.workspace_root)
        export_trading_summary(day, result["paths"])
        health = result["health"]
        status = "success" if not health.get("errors") else "failed"
        return {"date": day, "status": status, "error": None, "health": health}
    except Exception as exc:  # noqa: BLE001 - validation report must record operational failures.
        return {"date": day, "status": "failed", "error": str(exc), "health": load_health(day, paths)}


def _collect_totals(days: list[str], paths: ProjectPaths) -> dict[str, Any]:
    rejection_reasons: Counter[str] = Counter()
    totals = {
        "total_signals": 0,
        "total_orders": 0,
        "total_trades": 0,
        "rejected_orders": 0,
        "fallback_price_counts": 0,
        "stale_price_counts": 0,
        "missing_price_counts": 0,
        "evolution_proposal_count": 0,
        "experiment_queue_growth": 0,
    }
    queue_sizes = []
    for day in days:
        signals = read_jsonl(paths.dated_jsonl("signals", "trading_signals", day))
        orders = read_jsonl(paths.dated_jsonl("orders", "orders", day))
        trades = read_jsonl(paths.dated_jsonl("trades", "trades", day))
        health = load_health(day, paths) or {}
        evolution = read_json(paths.data_dir / "evolution" / f"evolution-summary-{day}.json", default={})
        queue_path = paths.data_dir / "experiments" / "experiment_queue.jsonl"
        if queue_path.exists():
            queue_sizes.append(len(read_jsonl(queue_path)))
        totals["total_signals"] += len(signals)
        totals["total_orders"] += len(orders)
        totals["total_trades"] += len(trades)
        rejected = [order for order in orders if order.get("status") == "rejected"]
        totals["rejected_orders"] += len(rejected)
        for order in rejected:
            rejection_reasons[str(order.get("risk_reason", "unknown"))] += 1
        totals["fallback_price_counts"] += int(health.get("fallback_prices_count", 0))
        totals["stale_price_counts"] += int(health.get("stale_prices_count", 0))
        totals["missing_price_counts"] += int(health.get("missing_prices_count", 0))
        totals["evolution_proposal_count"] += len(evolution.get("rule_memory", {}).get("rules", []))
    if len(queue_sizes) >= 2:
        totals["experiment_queue_growth"] = max(queue_sizes) - min(queue_sizes)
    totals["common_rejection_reasons"] = Counter(dict(rejection_reasons.most_common()))
    return totals


def _portfolio_continuity(days: list[str], paths: ProjectPaths) -> dict[str, Any]:
    missing = []
    discontinuities = []
    previous_total: float | None = None
    for day in days:
        portfolio = read_json(paths.dated_json("portfolios", "portfolio", day), default={})
        if not portfolio:
            missing.append(day)
            continue
        current_total = float(portfolio.get("total_asset", 0.0))
        if previous_total is not None and previous_total <= 0:
            discontinuities.append(f"{day}: previous total_asset is non-positive")
        previous_total = current_total
    return {"passed": not missing and not discontinuities, "missing_days": missing, "discontinuities": discontinuities}


def _shadow_contamination_status(audit: dict[str, Any]) -> dict[str, Any]:
    errors = [item for item in audit.get("critical_errors", []) if "shadow artifact" in str(item)]
    return {"passed": not errors, "errors": errors}


def _evolution_status(audit: dict[str, Any]) -> dict[str, Any]:
    errors = [item for item in audit.get("critical_errors", []) if "evolution proposals exceed throttle" in str(item)]
    return {"passed": not errors, "errors": errors}


def _release_blocking_reasons(
    actual_run_days: int,
    audit: dict[str, Any],
    duplicate_status: dict[str, Any],
    portfolio_status: dict[str, Any],
    shadow_status: dict[str, Any],
    evolution_status: dict[str, Any],
    missing_input_days: list[str],
) -> list[str]:
    reasons = []
    if actual_run_days < 30:
        reasons.append("actual_run_days_below_30")
    if audit.get("critical_errors"):
        reasons.append("audit_critical_errors")
    if not duplicate_status["passed"]:
        reasons.append("duplicate_order_or_trade")
    if not portfolio_status["passed"]:
        reasons.append("portfolio_not_continuous")
    if not shadow_status["passed"]:
        reasons.append("shadow_contamination")
    if not evolution_status["passed"]:
        reasons.append("evolution_throttle_exceeded")
    if missing_input_days:
        reasons.append("missing_real_global_briefing_inputs")
    return sorted(set(reasons))


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Dry Run Validation Report {payload['start_date']} to {payload['end_date']}",
        "",
        f"- dry_run_30d_passed: {payload['dry_run_30d_passed']}",
        f"- release_blocking_reasons: {payload['release_blocking_reasons']}",
        f"- expected_trading_days: {payload['expected_trading_days']}",
        f"- actual_run_days: {payload['actual_run_days']}",
        f"- missing_input_days: {payload['missing_input_days']}",
        f"- successful_days: {payload['successful_days']}",
        f"- failed_days: {payload['failed_days']}",
        f"- total_signals: {payload['total_signals']}",
        f"- total_orders: {payload['total_orders']}",
        f"- total_trades: {payload['total_trades']}",
        f"- rejected_orders: {payload['rejected_orders']}",
        f"- common_rejection_reasons: {payload['common_rejection_reasons']}",
        f"- fallback/stale/missing price counts: {payload['fallback_price_counts']}/{payload['stale_price_counts']}/{payload['missing_price_counts']}",
        f"- portfolio continuity status: {payload['portfolio_continuity_status']}",
        f"- duplicate order/trade status: {payload['duplicate_order_trade_status']}",
        f"- shadow contamination status: {payload['shadow_contamination_status']}",
        f"- evolution proposal count: {payload['evolution_proposal_count']}",
        f"- experiment queue growth: {payload['experiment_queue_growth']}",
        f"- audit passed: {payload['audit_passed']}",
        "",
        "## Critical Errors",
    ]
    lines.extend(f"- {item}" for item in payload["critical_errors"]) if payload["critical_errors"] else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in payload["warnings"]) if payload["warnings"] else lines.append("- none")
    return "\n".join(lines) + "\n"
