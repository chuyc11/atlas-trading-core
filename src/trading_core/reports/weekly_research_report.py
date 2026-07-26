"""Weekly trading research report for v0.5."""

from __future__ import annotations

from typing import Any

from trading_core.reports.research_common import (
    dates_between,
    default_paths,
    latest_json,
    read_json,
    read_jsonl_count,
    write_json_and_markdown,
)
from trading_core.storage.file_paths import ProjectPaths


def build_weekly_research_report(
    start_date: str,
    end_date: str,
    include_experiments: bool = False,
    include_ml_shadow: bool = False,
    include_mistakes: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    warnings: list[str] = []
    dates = dates_between(start_date, end_date)
    orders = sum(read_jsonl_count(paths.data_dir / "orders" / f"orders-{day}.jsonl") for day in dates)
    trades = sum(read_jsonl_count(paths.data_dir / "trades" / f"trades-{day}.jsonl") for day in dates)
    portfolio_days = sum(1 for day in dates if (paths.data_dir / "portfolios" / f"portfolio-{day}.json").exists())
    run_days = sum(1 for day in dates if (paths.outputs_dir / "daily" / f"virtual-trading-report-{day}.md").exists())
    if run_days == 0:
        warnings.append("No forward daily-run evidence found for this period.")
    rejected_orders = 0

    ml_shadow = {"available": False, "recommendation": None, "prediction_count": 0, "signal_count": 0, "model_id": None}
    if include_ml_shadow:
        leaderboard = latest_json(paths.data_dir / "shadow", "ml_shadow_leaderboard-*.json")
        if leaderboard:
            ml_shadow = {
                "available": True,
                "model_id": leaderboard.get("model_id"),
                "recommendation": leaderboard.get("shadow_recommendation") or leaderboard.get("recommendation"),
                "prediction_count": leaderboard.get("prediction_count", 0),
                "signal_count": leaderboard.get("signal_count", 0),
            }
        else:
            warnings.append("ML shadow leaderboard missing.")

    experiments = {"parameter_sweeps": 0, "comparisons": 0, "promotion_simulations": 0, "mistake_patterns": 0}
    mistake_patterns: list[dict[str, Any]] = []
    if include_experiments:
        exp_dir = paths.data_dir / "experiments"
        experiments["parameter_sweeps"] = len(list(exp_dir.glob("parameter_sweep-*.json"))) if exp_dir.exists() else 0
        experiments["comparisons"] = len([p for p in exp_dir.glob("strategy_comparison-*.json") if "smoke" not in p.name.lower() and "test" not in p.name.lower()]) if exp_dir.exists() else 0
        experiments["promotion_simulations"] = len([p for p in exp_dir.glob("promotion_simulation-*.json") if "smoke" not in p.name.lower() and "test" not in p.name.lower()]) if exp_dir.exists() else 0
        library = read_json(exp_dir / "mistake_pattern_library.json", default={}, warnings=warnings)
        patterns = library.get("patterns", []) if isinstance(library, dict) else []
        experiments["mistake_patterns"] = len(patterns)
        if include_mistakes:
            mistake_patterns = patterns
    elif include_mistakes:
        warnings.append("Mistake patterns requested without experiment artifacts.")

    payload = {
        "report_id": f"WEEKLY-{start_date.replace('-', '')}-{end_date.replace('-', '')}",
        "start_date": start_date,
        "end_date": end_date,
        "period_type": "weekly",
        "summary": {"overall_status": "watch", "critical_errors": 0, "warnings": warnings},
        "warnings": warnings,
        "trading": {
            "run_days": run_days,
            "orders": orders,
            "trades": trades,
            "rejected_orders": rejected_orders,
            "portfolio_days": portfolio_days,
            "notes": [] if run_days else ["No forward daily-run evidence found for this period."],
        },
        "risk": {"risk_events": 0, "drawdown_notes": [], "position_notes": []},
        "ml_shadow": ml_shadow,
        "experiments": experiments,
        "mistake_patterns": [
            {
                "pattern_type": p.get("pattern_type"),
                "severity": p.get("severity"),
                "evidence_count": p.get("evidence_count"),
                "suggested_action": p.get("suggested_action"),
            }
            for p in mistake_patterns
        ],
        "limitations": [
            "This is not an admission gate.",
            "This is not live trading validation.",
            "This does not validate forward 30d dry-run.",
            "Shadow and watch labels are not active promotion.",
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
    json_path = paths.data_dir / "reports" / f"weekly_research_summary-{start_date}-{end_date}.json"
    md_path = paths.outputs_dir / "reports" / f"WEEKLY_RESEARCH_REPORT-{start_date}-{end_date}.md"
    write_json_and_markdown(json_path, payload, md_path, build_weekly_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_weekly_markdown(payload: dict[str, Any]) -> str:
    ml = payload["ml_shadow"]
    exp = payload["experiments"]
    lines = [
        "# Weekly Trading Research Report",
        "",
        "## 1. Scope",
        f"- start_date: {payload['start_date']}",
        f"- end_date: {payload['end_date']}",
        "- period_type: weekly",
        "",
        "## 2. Executive Summary",
        f"- overall_status: {payload['summary']['overall_status']}",
        f"- critical_errors: {payload['summary']['critical_errors']}",
        f"- warnings: {payload['summary']['warnings']}",
        "",
        "## 3. Trading Activity",
        f"- run_days: {payload['trading']['run_days']}",
        f"- orders: {payload['trading']['orders']}",
        f"- trades: {payload['trading']['trades']}",
        f"- rejected_orders: {payload['trading']['rejected_orders']}",
        f"- portfolio continuity notes: {payload['trading']['notes']}",
        "",
        "## 4. Risk and Account Review",
        "- risk events: 0",
        "- drawdown notes: []",
        "- position notes: []",
        "",
        "## 5. ML Shadow Review",
        f"- model_id: {ml.get('model_id')}",
        f"- prediction_count: {ml.get('prediction_count')}",
        f"- signal_count: {ml.get('signal_count')}",
        f"- recommendation: {ml.get('recommendation')}",
        "- boundary: shadow only",
        "",
        "## 6. Experiment Review",
        f"- parameter sweep count: {exp['parameter_sweeps']}",
        f"- strategy comparison count: {exp['comparisons']}",
        f"- promotion simulation count: {exp['promotion_simulations']}",
        f"- mistake pattern count: {exp['mistake_patterns']}",
        "",
        "## 7. Mistake Patterns",
    ]
    if payload.get("mistake_patterns"):
        for pattern in payload["mistake_patterns"]:
            lines.append(f"- {pattern.get('pattern_type')} | severity={pattern.get('severity')} | evidence={pattern.get('evidence_count')} | action={pattern.get('suggested_action')}")
    else:
        lines.append("- No formal mistake patterns included.")
    lines.extend(
        [
            "",
            "## 8. Limitations",
            "- not an admission gate",
            "- not live trading",
            "- not forward 30d dry-run",
            "- not active promotion",
            "",
            "## 9. Safety Boundary",
            "- research_only=true",
            "- no orders/trades/portfolio/accounts written",
            "- no strategy state changed",
            "- no promotion triggered",
            "- This does not validate forward 30d dry-run.",
            "",
        ]
    )
    return "\n".join(lines)
