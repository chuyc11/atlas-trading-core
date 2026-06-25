"""Baseline strategy registry and parameter versions."""

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


PARAMETERS: dict[str, dict[str, Any]] = {
    "equal_weight_etf_rotation": {
        "top_n": 8,
        "rebalance_frequency": "weekly",
        "cash_buffer_pct": 0.02,
        "min_weight": 0.0,
        "max_weight": 0.20,
        "exclude_untradable": True,
    },
    "momentum_risk_adjusted_rotation": {
        "lookback_days": 60,
        "volatility_lookback_days": 60,
        "top_n": 4,
        "cash_buffer_pct": 0.03,
        "max_weight": 0.30,
        "risk_penalty": 0.5,
        "min_history_days": 60,
        "exclude_untradable": True,
    },
    "defensive_cash_rotation": {
        "risk_off_threshold": 0.65,
        "risk_on_threshold": 0.45,
        "max_equity_weight_risk_on": 0.95,
        "max_equity_weight_risk_off": 0.35,
        "cash_buffer_pct": 0.05,
        "top_n": 4,
        "fallback_to_cash_on_missing_risk": True,
    },
}


def build_baseline_strategy_registry(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    registry_id, created_at = timestamp_id("BASELINE-STRATEGY-REGISTRY")
    strategies = {}
    for strategy_id in STRATEGY_IDS:
        strategies[strategy_id] = {
            "strategy_id": strategy_id,
            "parameter_version": strategy_version(strategy_id),
            "strategy_type": "deterministic_rule_based",
            "universe": list(DEFAULT_UNIVERSE),
            "benchmarks": list(DEFAULT_BENCHMARKS),
            "parameters": PARAMETERS[strategy_id],
            "uses_ml": False,
            "uses_llm": False,
            "uses_rl": False,
            "uses_promotion_outputs": False,
            "starts_forward_dry_run": False,
            "isolated_replay_only": True,
        }
    payload: dict[str, Any] = {
        "registry_id": registry_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "strategies": strategies,
        "parameter_versions": {strategy_id: strategy_version(strategy_id) for strategy_id in STRATEGY_IDS},
        "boundary": research_boundary("registry_only"),
    }
    json_path = paths.data_dir / "strategies" / "baseline_strategy_registry.json"
    md_path = paths.outputs_dir / "strategies" / "BASELINE_STRATEGY_REGISTRY.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Strategy Registry",
        "",
        RESEARCH_NOTICE,
        "",
        "## Parameter Versions",
    ]
    lines.extend(f"- {strategy_id}: {version}" for strategy_id, version in payload["parameter_versions"].items())
    lines.extend(["", "## Boundary"])
    lines.extend(markdown_boundary("registry only"))
    lines.append("")
    return "\n".join(lines)

