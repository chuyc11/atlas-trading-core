"""Bind v0.6.0 baseline strategies to a one-day daily workflow signal artifact."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.baseline_signal_engine import _target_weights
from trading_core.strategies.common import load_price_history, load_risk_history, selected_strategies, strategy_version

from .common import DEFAULT_AS_OF_DATE, NOTICE, boundary_markdown, daily_signals_path, daily_signals_report_path, freeze_path, next_execution_date, paths_or_default, read_json_file, workflow_boundary, write_artifact
from .daily_input_freeze_manifest import build_daily_input_freeze_manifest


def build_daily_baseline_signals(*, as_of_date: str = DEFAULT_AS_OF_DATE, strategy: str = "all", paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if not freeze_path(paths, as_of_date).exists():
        build_daily_input_freeze_manifest(as_of_date=as_of_date, paths=paths)
    freeze = read_json_file(freeze_path(paths, as_of_date))
    prices, price_source = load_price_history(paths, start_date=as_of_date, end_date=as_of_date)
    risks, risk_source = load_risk_history(paths, start_date=as_of_date, end_date=as_of_date)
    execution_date = next_execution_date(as_of_date)
    signals = []
    for strategy_id in selected_strategies(strategy):
        target_weights, cash_weight, warnings, diagnostics = _target_weights(strategy_id, as_of_date, prices, risks)
        signal = {
            "strategy_id": strategy_id,
            "strategy_version": strategy_version(strategy_id),
            "signal_date": as_of_date,
            "generated_at": f"{as_of_date}T16:30:00+08:00",
            "execution_earliest_date": execution_date,
            "target_weights": target_weights,
            "cash_weight": cash_weight,
            "inputs": {
                "freeze_manifest": f"data/daily_workflow/freeze_manifests/daily_input_freeze_manifest-{as_of_date}.json",
                "price_data_as_of": diagnostics.get("price_data_as_of", as_of_date),
                "risk_data_as_of": diagnostics.get("risk_data_as_of"),
                "price_source": price_source["source"],
                "risk_source": risk_source["source"],
            },
            "warnings": warnings,
            "pit_constraints_passed": _pit_passed(as_of_date, execution_date, target_weights, cash_weight, diagnostics),
            "uses_ml_shadow": False,
            "uses_llm": False,
            "uses_rl": False,
            "uses_promotion_outputs": False,
        }
        signals.append(signal)
    payload: dict[str, Any] = {
        "as_of_date": as_of_date,
        "strategy": strategy,
        "signals": signals,
        "strategies_total": len(signals),
        "all_pit_constraints_passed": all(signal["pit_constraints_passed"] for signal in signals),
        "freeze_manifest": freeze.get("manifest_id"),
        "boundary": workflow_boundary("daily_baseline_signal_binding_only"),
    }
    return write_artifact(daily_signals_path(paths, as_of_date), payload, daily_signals_report_path(paths, as_of_date), build_markdown(payload))


def _pit_passed(as_of_date: str, execution_date: str, target_weights: dict[str, float], cash_weight: float, diagnostics: dict[str, Any]) -> bool:
    no_future_inputs = all(value is None or str(value) <= as_of_date for value in [diagnostics.get("price_data_as_of"), diagnostics.get("risk_data_as_of")])
    return execution_date > as_of_date and no_future_inputs and cash_weight >= 0 and all(weight >= 0 for weight in target_weights.values()) and sum(target_weights.values()) + cash_weight <= 1.000001


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Baseline Signals - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Signals",
    ]
    lines.extend(f"- {signal['strategy_id']}: execution_earliest_date={signal['execution_earliest_date']}" for signal in payload["signals"])
    lines.extend(["", "## Boundary"])
    lines.extend(boundary_markdown("daily baseline signal binding only"))
    lines.append("")
    return "\n".join(lines)

