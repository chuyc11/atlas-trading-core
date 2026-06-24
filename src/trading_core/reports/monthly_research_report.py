"""Monthly trading research report for v0.5."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from trading_core.reports.research_common import default_paths, latest_json, read_json, read_jsonl_count, write_json_and_markdown
from trading_core.storage.file_paths import ProjectPaths


def month_range(month: str) -> tuple[str, str]:
    year, mon = map(int, month.split("-"))
    start = date(year, mon, 1)
    next_month = date(year + (mon == 12), 1 if mon == 12 else mon + 1, 1)
    return start.isoformat(), (next_month - timedelta(days=1)).isoformat()


def build_monthly_research_report(
    start_date: str | None = None,
    end_date: str | None = None,
    month: str | None = None,
    include_weekly: bool = False,
    include_experiments: bool = False,
    include_ml_shadow: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if month:
        start_date, end_date = month_range(month)
    if not start_date or not end_date:
        raise ValueError("start_date/end_date or month is required")
    warnings: list[str] = []
    weekly_files = sorted((paths.data_dir / "reports").glob(f"weekly_research_summary-*.json")) if (paths.data_dir / "reports").exists() else []
    weekly_payloads = [
        payload for payload in (read_json(path, default=None) for path in weekly_files)
        if isinstance(payload, dict) and start_date <= payload.get("start_date", "") <= end_date
    ]
    if include_weekly and not weekly_payloads:
        warnings.append("No weekly research summaries found for this period.")

    orders = sum(int(item.get("trading", {}).get("orders", 0)) for item in weekly_payloads)
    trades = sum(int(item.get("trading", {}).get("trades", 0)) for item in weekly_payloads)
    run_days = sum(int(item.get("trading", {}).get("run_days", 0)) for item in weekly_payloads)
    if not weekly_payloads:
        warnings.append("Monthly report generated from artifacts because weekly summaries are missing.")

    ml_shadow = {"available": False, "recommendations": []}
    if include_ml_shadow:
        leaderboard = latest_json(paths.data_dir / "shadow", "ml_shadow_leaderboard-*.json")
        if leaderboard:
            ml_shadow = {"available": True, "recommendations": [leaderboard.get("shadow_recommendation") or leaderboard.get("recommendation")]}
        else:
            warnings.append("ML shadow leaderboard missing.")

    exp_dir = paths.data_dir / "experiments"
    library = read_json(exp_dir / "mistake_pattern_library.json", default={})
    registry = read_json(exp_dir / "experiment_registry.json", default={})
    experiments = {
        "experiment_count": len(registry.get("experiments", [])) if isinstance(registry, dict) else 0,
        "sweep_count": len(list(exp_dir.glob("parameter_sweep-*.json"))) if exp_dir.exists() and include_experiments else 0,
        "comparison_count": len([p for p in exp_dir.glob("strategy_comparison-*.json") if "smoke" not in p.name.lower() and "test" not in p.name.lower()]) if exp_dir.exists() and include_experiments else 0,
        "promotion_simulation_count": len([p for p in exp_dir.glob("promotion_simulation-*.json") if "smoke" not in p.name.lower() and "test" not in p.name.lower()]) if exp_dir.exists() and include_experiments else 0,
        "mistake_pattern_count": len(library.get("patterns", [])) if isinstance(library, dict) and include_experiments else 0,
    }
    payload = {
        "report_id": f"MONTHLY-{start_date[:7].replace('-', '')}",
        "start_date": start_date,
        "end_date": end_date,
        "period_type": "monthly",
        "weekly_reports": {"count": len(weekly_payloads), "missing_weeks": [] if weekly_payloads else ["weekly summaries missing"]},
        "summary": {"overall_status": "watch", "critical_errors": 0, "warnings": warnings},
        "warnings": warnings,
        "trading": {"run_days": run_days, "orders": orders, "trades": trades, "notes": []},
        "ml_shadow": ml_shadow,
        "experiments": experiments,
        "research_conclusions": [
            "No strategy is eligible for active promotion.",
            "Current evidence supports continued shadow observation only.",
        ],
        "boundary": {
            "research_only": True,
            "write_main_ledger": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "reports" / f"monthly_research_summary-{start_date}-{end_date}.json"
    md_path = paths.outputs_dir / "reports" / f"MONTHLY_RESEARCH_REPORT-{start_date}-{end_date}.md"
    write_json_and_markdown(json_path, payload, md_path, build_monthly_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_monthly_markdown(payload: dict[str, Any]) -> str:
    exp = payload["experiments"]
    lines = [
        "# Monthly Trading Research Report",
        "",
        "## 1. Scope",
        f"- start_date: {payload['start_date']}",
        f"- end_date: {payload['end_date']}",
        "- period_type: monthly",
        "",
        "## 2. Monthly Summary",
        f"- overall_status: {payload['summary']['overall_status']}",
        f"- critical_errors: {payload['summary']['critical_errors']}",
        f"- warnings: {payload['summary']['warnings']}",
        "",
        "## 3. Weekly Report Coverage",
        f"- weekly report count: {payload['weekly_reports']['count']}",
        f"- missing weeks: {payload['weekly_reports']['missing_weeks']}",
        "",
        "## 4. Trading and Risk Review",
        f"- run days: {payload['trading']['run_days']}",
        f"- orders: {payload['trading']['orders']}",
        f"- trades: {payload['trading']['trades']}",
        "- risk notes: []",
        "",
        "## 5. ML Shadow Review",
        f"- recommendations: {payload['ml_shadow']['recommendations']}",
        "- limitations: shadow-only research, not live trading",
        "",
        "## 6. Strategy Experiment Review",
        f"- sweep count: {exp['sweep_count']}",
        f"- comparison count: {exp['comparison_count']}",
        f"- promotion simulation count: {exp['promotion_simulation_count']}",
        f"- mistake pattern count: {exp['mistake_pattern_count']}",
        "",
        "## 7. Research Conclusions",
        "- no active promotion unless validated",
        "- shadow-only observations",
        "",
        "## 8. Safety Boundary",
        "- research only",
        "- no live trading",
        "- no broker",
        "- not an admission gate",
        "- no active promotion",
        "- no orders/trades/portfolio/accounts written",
        "- does not validate forward 30d dry-run",
        "",
    ]
    return "\n".join(lines)
