"""Machine-readable contract for deterministic baseline strategies."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown

from .common import (
    DEFAULT_BENCHMARKS,
    DEFAULT_UNIVERSE,
    RELEASE_CANDIDATE,
    RESEARCH_NOTICE,
    STRATEGY_IDS,
    markdown_boundary,
    paths_or_default,
    research_boundary,
    strategy_version,
)


def build_baseline_strategy_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("BASELINE-STRATEGY-CONTRACT-V1")
    strategies = {strategy_id: _strategy_contract(strategy_id) for strategy_id in STRATEGY_IDS}
    payload: dict[str, Any] = {
        "contract_id": "BASELINE-STRATEGY-CONTRACT-V1",
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "strategies": strategies,
        "boundary": research_boundary("contract_only"),
    }
    json_path = paths.data_dir / "strategies" / "baseline_strategy_contract.json"
    md_path = paths.outputs_dir / "strategies" / "BASELINE_STRATEGY_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _strategy_contract(strategy_id: str) -> dict[str, Any]:
    return {
        "strategy_id": strategy_id,
        "display_name": strategy_id.replace("_", " ").title(),
        "version": strategy_version(strategy_id),
        "strategy_type": "deterministic_rule_based",
        "universe": list(DEFAULT_UNIVERSE),
        "benchmark": list(DEFAULT_BENCHMARKS),
        "input_artifacts": [
            "data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv",
            "data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl",
            "data/system/ashare_price_status_contract.json",
            "data/system/ashare_trading_calendar_contract.json",
            "data/strategies/baseline_strategy_registry.json",
        ],
        "signal_timing": "after_t_close",
        "execution_timing": "t_plus_1",
        "parameter_schema": {"version": "string", "parameters": "object"},
        "output_signal_schema": {
            "strategy_id": "string",
            "strategy_version": "string",
            "signal_date": "YYYY-MM-DD",
            "generated_at": "ISO-8601 after market close",
            "execution_earliest_date": "YYYY-MM-DD next trading day or later",
            "target_weights": "symbol to non-negative float",
            "cash_weight": "non-negative float",
        },
        "target_weight_schema": {
            "sum_target_weights_plus_cash_lte_one": True,
            "no_negative_weights": True,
            "untradable_symbols_weight_zero_or_excluded": True,
        },
        "risk_controls": [
            "max_weight",
            "cash_buffer_pct",
            "exclude_untradable",
            "isolated_replay_only",
        ],
        "pit_constraints": [
            "signals only use data available on or before signal_date",
            "risk proxy data must be as_of signal_date or earlier",
            "execution earliest date must be next trading day or later",
            "no labels, ML shadow, promotion outputs, LLM, or RL inputs",
        ],
        "forbidden_inputs": [
            "future_prices",
            "future_risk_signals",
            "labels_as_authorization",
            "ml_shadow_as_authorization",
            "llm_trading_decision",
            "rl_policy",
            "promotion_outputs",
        ],
        "forbidden_claims": [
            "strategy effectiveness proven",
            "forward dry-run validated",
            "live trading ready",
        ],
        "isolated_replay_only": True,
        "no_promotion": True,
        "uses_ml_shadow": False,
        "uses_llm": False,
        "uses_rl": False,
        "uses_promotion_outputs": False,
        "starts_forward_dry_run": False,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Strategy Contract",
        "",
        RESEARCH_NOTICE,
        "",
        "## Strategies",
    ]
    for strategy_id, contract in payload["strategies"].items():
        lines.extend(
            [
                f"- {strategy_id}: {contract['version']}",
                "  - deterministic rule-based",
                "  - after T close signal, T+1 execution",
                "  - isolated replay only",
                "  - not strategy effectiveness proof",
                "  - not forward dry-run validation",
                "  - not live trading readiness",
            ]
        )
    lines.extend(["", "## Boundary"])
    lines.extend(markdown_boundary("contract only"))
    lines.append("")
    return "\n".join(lines)

