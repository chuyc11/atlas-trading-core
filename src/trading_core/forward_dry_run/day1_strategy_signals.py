"""Generate day 1 baseline strategy signals for forward dry-run."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, boundary, day_json, day_report, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_input_snapshot import build_day1_input_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.baseline_signal_engine import _target_weights
from trading_core.strategies.common import STRATEGY_IDS, load_price_history, load_risk_history, next_execution_date, strategy_version


def build_day1_strategy_signals(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    snapshot_path = day_json(paths, "day1_input_snapshot.json")
    if not snapshot_path.exists():
        build_day1_input_snapshot(paths=paths)
    snapshot = read_json_file(snapshot_path)
    as_of_date = str(snapshot["as_of_date"])
    prices, price_source = load_price_history(paths, start_date=as_of_date, end_date=as_of_date)
    risks, risk_source = load_risk_history(paths, start_date=as_of_date, end_date=as_of_date)
    execution_date = next_execution_date(as_of_date)
    signals = []
    for strategy_id in STRATEGY_IDS:
        target_weights, cash_weight, warnings, diagnostics = _target_weights(strategy_id, as_of_date, prices, risks)
        signals.append(
            {
                "strategy_id": strategy_id,
                "strategy_version": strategy_version(strategy_id),
                "signal_date": as_of_date,
                "execution_earliest_date": execution_date,
                "target_weights": target_weights,
                "cash_weight": cash_weight,
                "warnings": warnings,
                "diagnostics": diagnostics,
                "inputs": {"price_source": price_source["source"], "risk_source": risk_source["source"]},
                "no_future_price_data": str(diagnostics.get("price_data_as_of") or as_of_date) <= as_of_date,
                "no_future_risk_proxy": str(diagnostics.get("risk_data_as_of") or as_of_date) <= as_of_date,
                "uses_ml_shadow": False,
                "uses_llm": False,
                "uses_rl": False,
                "uses_promotion_outputs": False,
            }
        )
    payload: dict[str, Any] = {
        "signals_id": "FORWARD-DRY-RUN-DAY1-STRATEGY-SIGNALS",
        "day_index": DAY_INDEX,
        "as_of_date": as_of_date,
        "strategies_total": len(STRATEGY_IDS),
        "strategies_generated": len(signals),
        "signals": signals,
        "boundary": boundary("baseline_strategies_only"),
    }
    payload["boundary"]["baseline_strategies_only"] = True
    return write_artifact(day_json(paths, "day1_strategy_signals.json"), payload, day_report(paths, "DAY1_STRATEGY_SIGNALS.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Strategy Signals",
        "",
        f"- as_of_date: {payload['as_of_date']}",
        f"- strategies_generated: {payload['strategies_generated']}",
        "",
        "## Strategies",
    ]
    lines.extend(f"- {signal['strategy_id']}: execution_earliest_date={signal['execution_earliest_date']}" for signal in payload["signals"])
    lines.extend(["", "## Boundary", *non_claim_lines(), ""])
    return "\n".join(lines)

