"""Research reports for baseline strategies."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import write_json_markdown

from .baseline_benchmark_comparison import compare_baseline_strategy_benchmarks
from .baseline_strategy_registry import build_baseline_strategy_registry
from .baseline_strategy_replay import replay_baseline_strategy
from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    DEFAULT_UNIVERSE,
    RESEARCH_NOTICE,
    benchmark_path,
    paths_or_default,
    read_dict,
    replay_summary_path,
    report_markdown_path,
    report_path,
    research_boundary,
    selected_strategies,
    strategy_version,
)


EXPLICIT_NON_CLAIMS = [
    "This is not strategy effectiveness proof.",
    "This is not forward dry-run validation.",
    "This is not live trading readiness.",
    "This does not trigger promotion.",
    "This does not use ML/LLM/RL for trading decisions.",
]


def build_baseline_strategy_report(
    *,
    strategy: str = "all",
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if not (paths.data_dir / "strategies" / "baseline_strategy_registry.json").exists():
        build_baseline_strategy_registry(paths=paths)
    for strategy_id in selected_strategies(strategy):
        if not replay_summary_path(paths, strategy_id, start_date, end_date).exists():
            replay_baseline_strategy(strategy=strategy_id, start_date=start_date, end_date=end_date, execution_mode="isolated", paths=paths)
    if not benchmark_path(paths, start_date, end_date).exists():
        compare_baseline_strategy_benchmarks(strategy="all", start_date=start_date, end_date=end_date, paths=paths)
    registry = read_dict(paths.data_dir / "strategies" / "baseline_strategy_registry.json")
    comparison = read_dict(benchmark_path(paths, start_date, end_date))
    outputs = {}
    for strategy_id in selected_strategies(strategy):
        replay = read_dict(replay_summary_path(paths, strategy_id, start_date, end_date))
        payload = _report_payload(strategy_id, start_date, end_date, registry, replay, comparison)
        json_path = report_path(paths, strategy_id, start_date, end_date)
        md_path = report_markdown_path(paths, strategy_id, start_date, end_date)
        write_json_markdown(json_path, payload, md_path, build_markdown(payload))
        outputs[strategy_id] = {"json_path": str(json_path), "report_path": str(md_path), "explicit_non_claims": payload["explicit_non_claims"]}
    return {
        "strategy": strategy,
        "start_date": start_date,
        "end_date": end_date,
        "paths": outputs,
        "all_reports_generated": all(outputs),
        "boundary": research_boundary("strategy_report_only"),
    }


def _report_payload(
    strategy_id: str,
    start_date: str,
    end_date: str,
    registry: dict[str, Any],
    replay: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    strategy_registry = registry.get("strategies", {}).get(strategy_id, {})
    benchmark_metrics = comparison.get("strategies", {}).get(strategy_id, {})
    return {
        "report_id": f"BASELINE-STRATEGY-REPORT-{strategy_id}-{start_date}-{end_date}",
        "strategy_id": strategy_id,
        "strategy_version": strategy_version(strategy_id),
        "strategy_objective": _objective(strategy_id),
        "parameter_version": strategy_registry.get("parameter_version"),
        "parameters": strategy_registry.get("parameters", {}),
        "universe": strategy_registry.get("universe", list(DEFAULT_UNIVERSE)),
        "inputs": {
            "registry": "data/strategies/baseline_strategy_registry.json",
            "replay_summary": f"data/replays/strategies/{strategy_id}/replay-{start_date}-{end_date}.json",
            "benchmark_comparison": f"data/strategies/benchmark_comparison/baseline_benchmark_comparison-{start_date}-{end_date}.json",
        },
        "pit_constraints": [
            "uses signal_date or earlier price data",
            "uses signal_date or earlier risk proxy data",
            "generated after T close",
            "execution earliest date is T+1 or later",
        ],
        "replay_summary": {
            "orders": replay.get("orders", 0),
            "trades": replay.get("trades", 0),
            "rejected_orders": replay.get("rejected_orders", 0),
            "no_trade_fallback": replay.get("no_trade_fallback", False),
        },
        "benchmark_comparison": benchmark_metrics,
        "execution_summary": {
            "execution_mode": replay.get("execution_mode"),
            "uses_v059_virtual_execution_contract": replay.get("uses_v059_virtual_execution_contract"),
            "isolated_outputs_only": True,
        },
        "rejected_orders": {
            "count": replay.get("rejected_orders", 0),
            "reasons": replay.get("rejected_order_reasons", []),
        },
        "cost_summary": replay.get("cost_summary", {}),
        "drawdown_summary": {"max_drawdown": benchmark_metrics.get("max_drawdown")},
        "known_limitations": [
            "historical replay uses isolated research ledgers only",
            "benchmark mapping uses configured ETF proxies when direct index series are unavailable",
            "short replay sample is a readiness artifact, not a forward validation result",
        ],
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
        "promotion_triggered": False,
        "uses_ml_shadow": False,
        "uses_llm": False,
        "uses_rl": False,
        "boundary": research_boundary("strategy_report_only"),
    }


def _objective(strategy_id: str) -> str:
    objectives = {
        "equal_weight_etf_rotation": "Maintain an equal-weight ETF baseline across tradable universe members.",
        "momentum_risk_adjusted_rotation": "Rank tradable ETFs by trailing return minus a volatility penalty.",
        "defensive_cash_rotation": "Shift between ETF exposure and cash based on a global risk proxy.",
    }
    return objectives[strategy_id]


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Baseline Strategy Report - {payload['strategy_id']}",
        "",
        RESEARCH_NOTICE,
        "",
        "## Strategy",
        f"- strategy_id: {payload['strategy_id']}",
        f"- strategy_version: {payload['strategy_version']}",
        f"- objective: {payload['strategy_objective']}",
        "",
        "## PIT Constraints",
    ]
    lines.extend(f"- {item}" for item in payload["pit_constraints"])
    lines.extend(["", "## Replay Summary"])
    lines.extend(f"- {key}: {value}" for key, value in payload["replay_summary"].items())
    lines.extend(["", "## Benchmark Comparison", f"- cumulative_return: {payload['benchmark_comparison'].get('cumulative_return')}", f"- max_drawdown: {payload['benchmark_comparison'].get('max_drawdown')}", "", "## Execution Summary"])
    lines.extend(f"- {key}: {value}" for key, value in payload["execution_summary"].items())
    lines.extend(["", "## Explicit Non-Claims"])
    lines.extend(f"- {item}" for item in payload["explicit_non_claims"])
    lines.extend(["", "## Boundary", "- strategy report only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)
