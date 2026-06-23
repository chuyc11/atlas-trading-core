from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from trading_core.backtest.event_backtester import date_range
from trading_core.daily_run import run_daily
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.runtime.health import load_health, summarize_health
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


def run_dry_run_range(
    start_date: str,
    end_date: str,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    paths = project_paths(workspace_root)
    days = date_range(start_date, end_date)
    day_results = []
    for day in days:
        try:
            result = run_daily(day, paths.workspace_root)
            export_trading_summary(day, result["paths"])
            health = result["health"]
            status = "success" if not health.get("errors") else "failed"
            error = None
        except Exception as exc:  # pragma: no cover - exercised by operational runs.
            health = load_health(day, paths) or {}
            status = "failed"
            error = str(exc)
        day_results.append({"date": day, "status": status, "error": error, "health": health})

    health_summary = summarize_health(start_date, end_date, paths)
    reject_reasons = _reject_reasons(paths, days)
    asset_curve = [
        {
            "date": row["date"],
            "total_asset": row.get("health", {}).get("portfolio_total_asset"),
        }
        for row in day_results
        if row.get("health", {}).get("portfolio_total_asset") is not None
    ]
    payload = {
        **health_summary,
        "scheduled_trading_days": len(days),
        "day_results": day_results,
        "total_signals_count": sum(int(row.get("health", {}).get("trading_signals_count", 0)) for row in day_results),
        "most_common_rejected_reason": reject_reasons.most_common(1)[0][0] if reject_reasons else health_summary.get("most_common_rejected_reason"),
        "asset_curve": asset_curve,
        "evolution_proposals_count": health_summary.get("evolution_proposal_count", 0),
        "experiments_new_count": health_summary.get("experiment_queue_growth_count", 0),
    }
    output_dir = paths.outputs_dir / "dry-runs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"DRY_RUN_SUMMARY-{start_date}-{end_date}.md"
    json_path = paths.data_dir / "runtime" / f"dry-run-summary-{start_date}-to-{end_date}.json"
    write_json(json_path, payload)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    return payload


def _reject_reasons(paths, days: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for day in days:
        for order in read_jsonl(paths.dated_jsonl("orders", "orders", day)):
            if order.get("status") == "rejected":
                counter[str(order.get("risk_reason", "unknown"))] += 1
    return counter


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Dry Run Summary {payload['start_date']} to {payload['end_date']}",
        "",
        f"- Scheduled trading days: {payload['scheduled_trading_days']}",
        f"- Success days: {payload['success_days']}",
        f"- Failed days: {payload['failed_days']}",
        f"- Total signals: {payload['total_signals_count']}",
        f"- Total orders: {payload['total_orders_count']}",
        f"- Total trades: {payload['total_trades_count']}",
        f"- Total rejections: {payload['total_rejected_orders_count']}",
        f"- Most common reject: {payload['most_common_rejected_reason']}",
        f"- Fallback prices: {payload['fallback_prices_count']}",
        f"- Stale prices: {payload['stale_prices_count']}",
        f"- Missing prices: {payload['missing_prices_count']}",
        f"- Missing input files: {payload['missing_input_count']}",
        f"- Max daily asset change: {payload['max_daily_asset_change']}",
        f"- Total asset change: {payload['total_asset_change']}",
        f"- Evolution proposals: {payload['evolution_proposals_count']}",
        f"- Experiments new: {payload['experiments_new_count']}",
        "",
        "## Asset Curve",
    ]
    if payload["asset_curve"]:
        lines.extend(f"- {row['date']}: {row['total_asset']}" for row in payload["asset_curve"])
    else:
        lines.append("- none")
    lines.extend(["", "## Daily Status"])
    for row in payload["day_results"]:
        suffix = f" ({row['error']})" if row.get("error") else ""
        lines.append(f"- {row['date']}: {row['status']}{suffix}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()
    result = run_dry_run_range(args.start_date, args.end_date)
    print(result["report_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
