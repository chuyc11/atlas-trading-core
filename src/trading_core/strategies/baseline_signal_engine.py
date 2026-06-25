"""PIT-safe deterministic baseline strategy signal generation."""

from __future__ import annotations

from statistics import pstdev
from typing import Any

from trading_core.execution.ashare_tradability import evaluate_tradability
from trading_core.storage.file_paths import ProjectPaths

from .baseline_strategy_registry import PARAMETERS, build_baseline_strategy_registry
from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    DEFAULT_UNIVERSE,
    RESEARCH_NOTICE,
    load_price_history,
    load_risk_history,
    next_execution_date,
    paths_or_default,
    price_on_or_before,
    read_dict,
    rel,
    research_boundary,
    rows_and_paths,
    selected_strategies,
    signal_path,
    signal_report_path,
    simulated_price_status,
    strategy_version,
    trading_dates,
    trailing_return,
    returns_for_symbol,
    latest_on_or_before,
)


def generate_baseline_strategy_signals(
    *,
    strategy: str = "all",
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    registry_path = paths.data_dir / "strategies" / "baseline_strategy_registry.json"
    registry = read_dict(registry_path)
    if not registry:
        registry = build_baseline_strategy_registry(paths=paths)
    prices, price_source = load_price_history(paths, start_date=start_date, end_date=end_date)
    risks, risk_source = load_risk_history(paths, start_date=start_date, end_date=end_date)
    selected = selected_strategies(strategy)
    outputs = {}
    for strategy_id in selected:
        rows = _strategy_rows(strategy_id, start_date, end_date, prices, risks, price_source, risk_source)
        jsonl_path = signal_path(paths, strategy_id, start_date, end_date)
        rows_and_paths(jsonl_path, rows)
        md_path = signal_report_path(paths, strategy_id, start_date, end_date)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(_build_markdown(strategy_id, rows, jsonl_path, paths), encoding="utf-8")
        outputs[strategy_id] = {
            "signal_path": str(jsonl_path),
            "report_path": str(md_path),
            "signals": len(rows),
            "warnings": sum(len(row.get("warnings", [])) for row in rows),
            "pit_constraints_passed": all(row.get("pit_constraints_passed") is True for row in rows),
        }
    return {
        "strategy": strategy,
        "start_date": start_date,
        "end_date": end_date,
        "strategies": selected,
        "paths": outputs,
        "all_signals_generated": all(item["signals"] > 0 for item in outputs.values()),
        "all_pit_constraints_passed": all(item["pit_constraints_passed"] for item in outputs.values()),
        "boundary": research_boundary("signal_generation_only"),
    }


def _strategy_rows(
    strategy_id: str,
    start_date: str,
    end_date: str,
    prices: dict[str, dict[str, float]],
    risks: dict[str, float],
    price_source: dict[str, Any],
    risk_source: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for signal_date in trading_dates(start_date, end_date):
        target_weights, cash_weight, warnings, diagnostics = _target_weights(strategy_id, signal_date, prices, risks)
        execution_date = next_execution_date(signal_date)
        row = {
            "strategy_id": strategy_id,
            "strategy_version": strategy_version(strategy_id),
            "signal_date": signal_date,
            "generated_at": f"{signal_date}T16:30:00+08:00",
            "execution_earliest_date": execution_date,
            "target_weights": target_weights,
            "cash_weight": cash_weight,
            "inputs": {
                "price_data_as_of": diagnostics.get("price_data_as_of", signal_date),
                "risk_data_as_of": diagnostics.get("risk_data_as_of"),
                "price_source": price_source["source"],
                "risk_source": risk_source["source"],
                "price_fallback_used": price_source["fallback_used"],
                "risk_fallback_used": risk_source["fallback_used"],
            },
            "warnings": warnings,
            "pit_constraints_passed": _pit_passed(signal_date, execution_date, target_weights, cash_weight, diagnostics),
            "uses_ml_shadow": False,
            "uses_llm": False,
            "uses_rl": False,
            "uses_promotion_outputs": False,
            "boundary": {
                "after_t_close_signal": True,
                "t_plus_1_execution": True,
                "isolated_replay_only": True,
                "forward_dry_run_started": False,
            },
        }
        rows.append(row)
    return rows


def _target_weights(
    strategy_id: str,
    signal_date: str,
    prices: dict[str, dict[str, float]],
    risks: dict[str, float],
) -> tuple[dict[str, float], float, list[str], dict[str, Any]]:
    params = PARAMETERS[strategy_id]
    if strategy_id == "equal_weight_etf_rotation":
        return _equal_weights(signal_date, prices, params)
    if strategy_id == "momentum_risk_adjusted_rotation":
        return _momentum_weights(signal_date, prices, params)
    return _defensive_weights(signal_date, prices, risks, params)


def _tradable_symbols(signal_date: str, prices: dict[str, dict[str, float]]) -> tuple[list[str], str]:
    selected = []
    latest_dates = []
    for symbol in DEFAULT_UNIVERSE:
        price_date, price = price_on_or_before(prices, symbol, signal_date)
        if price_date:
            latest_dates.append(price_date)
        decision = evaluate_tradability(
            simulated_price_status(symbol, signal_date),
            "BUY",
            price_available=price is not None,
            status_date=signal_date,
            execution_date=signal_date,
        )
        if decision.allowed:
            selected.append(symbol)
    return selected, max(latest_dates) if latest_dates else signal_date


def _equal_weights(signal_date: str, prices: dict[str, dict[str, float]], params: dict[str, Any]) -> tuple[dict[str, float], float, list[str], dict[str, Any]]:
    tradable, price_as_of = _tradable_symbols(signal_date, prices)
    top = tradable[: int(params["top_n"])]
    if not top:
        return {}, 1.0, ["no_tradable_symbols_fallback_to_cash"], {"price_data_as_of": price_as_of}
    target_total = 1.0 - float(params["cash_buffer_pct"])
    raw_weight = target_total / len(top)
    weight = min(float(params["max_weight"]), raw_weight)
    target_weights = {symbol: round(weight, 6) for symbol in top}
    cash_weight = round(1.0 - sum(target_weights.values()), 6)
    return target_weights, cash_weight, [], {"price_data_as_of": price_as_of}


def _momentum_weights(signal_date: str, prices: dict[str, dict[str, float]], params: dict[str, Any]) -> tuple[dict[str, float], float, list[str], dict[str, Any]]:
    tradable, price_as_of = _tradable_symbols(signal_date, prices)
    scored = []
    warnings = []
    lookback = int(params["lookback_days"])
    for symbol in tradable:
        symbol_return = trailing_return(prices, symbol, signal_date, lookback)
        symbol_returns = returns_for_symbol(prices, symbol, signal_date, int(params["volatility_lookback_days"]))
        if symbol_return is None or len(symbol_returns) < int(params["min_history_days"]):
            continue
        volatility = pstdev(symbol_returns) if len(symbol_returns) > 1 else 0.0
        score = symbol_return - float(params["risk_penalty"]) * volatility
        scored.append((score, symbol))
    if not scored:
        warnings.append("min_history_not_met_fallback_to_cash")
        return {}, 1.0, warnings, {"price_data_as_of": price_as_of}
    top = [symbol for _, symbol in sorted(scored, reverse=True)[: int(params["top_n"])]]
    target_total = 1.0 - float(params["cash_buffer_pct"])
    weight = min(float(params["max_weight"]), target_total / len(top))
    target_weights = {symbol: round(weight, 6) for symbol in top}
    cash_weight = round(1.0 - sum(target_weights.values()), 6)
    return target_weights, cash_weight, warnings, {"price_data_as_of": price_as_of}


def _defensive_weights(
    signal_date: str,
    prices: dict[str, dict[str, float]],
    risks: dict[str, float],
    params: dict[str, Any],
) -> tuple[dict[str, float], float, list[str], dict[str, Any]]:
    tradable, price_as_of = _tradable_symbols(signal_date, prices)
    risk_as_of, risk_value = latest_on_or_before(risks, signal_date)
    warnings = []
    if risk_value is None:
        if params["fallback_to_cash_on_missing_risk"]:
            warnings.append("missing_risk_proxy_fallback_to_cash")
            return {}, 1.0, warnings, {"price_data_as_of": price_as_of, "risk_data_as_of": None}
        risk_value = float(params["risk_on_threshold"])
    if risk_value >= float(params["risk_off_threshold"]):
        equity_weight = float(params["max_equity_weight_risk_off"])
    elif risk_value <= float(params["risk_on_threshold"]):
        equity_weight = float(params["max_equity_weight_risk_on"])
    else:
        midpoint = (float(params["max_equity_weight_risk_on"]) + float(params["max_equity_weight_risk_off"])) / 2
        equity_weight = midpoint
    top = tradable[: int(params["top_n"])]
    if not top:
        return {}, 1.0, ["no_tradable_symbols_fallback_to_cash"], {"price_data_as_of": price_as_of, "risk_data_as_of": risk_as_of}
    target_total = min(equity_weight, 1.0 - float(params["cash_buffer_pct"]))
    weight = target_total / len(top)
    target_weights = {symbol: round(weight, 6) for symbol in top}
    cash_weight = round(1.0 - sum(target_weights.values()), 6)
    return target_weights, cash_weight, warnings, {"price_data_as_of": price_as_of, "risk_data_as_of": risk_as_of, "risk_value": risk_value}


def _pit_passed(
    signal_date: str,
    execution_date: str,
    target_weights: dict[str, float],
    cash_weight: float,
    diagnostics: dict[str, Any],
) -> bool:
    no_future_inputs = all(
        value is None or str(value) <= signal_date
        for value in [diagnostics.get("price_data_as_of"), diagnostics.get("risk_data_as_of")]
    )
    return (
        execution_date > signal_date
        and no_future_inputs
        and cash_weight >= 0
        and all(weight >= 0 for weight in target_weights.values())
        and sum(target_weights.values()) + cash_weight <= 1.000001
    )


def _build_markdown(strategy_id: str, rows: list[dict[str, Any]], jsonl_path, paths: ProjectPaths) -> str:
    lines = [
        f"# Baseline Signals - {strategy_id}",
        "",
        RESEARCH_NOTICE,
        "",
        "## Summary",
        f"- rows: {len(rows)}",
        f"- path: {rel(jsonl_path, paths)}",
        f"- pit_constraints_passed: {str(all(row['pit_constraints_passed'] for row in rows)).lower()}",
        "",
        "## Boundary",
        "- signal generation only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
        "",
    ]
    return "\n".join(lines)

