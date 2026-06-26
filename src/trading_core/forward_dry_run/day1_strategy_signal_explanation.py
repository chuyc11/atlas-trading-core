"""Explain day1 baseline strategy signals for the owner report pack."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import build_simple_markdown, load_day1_owner_report_context, paths_or_default, report_boundary, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


STRATEGY_POSITIONING = {
    "equal_weight_etf_rotation": "Diversified baseline allocation across the ETF universe with a small cash reserve.",
    "momentum_risk_adjusted_rotation": "Baseline rotation that tilts toward stronger price momentum while keeping risk controls explicit.",
    "defensive_cash_rotation": "Defensive baseline allocation that keeps more cash when risk signals are elevated.",
}


def build_day1_strategy_signal_explanation(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    signals_payload = context["payloads"].get("day1_strategy_signals", {})
    explanations = []
    for signal in signals_payload.get("signals", []):
        strategy_id = signal.get("strategy_id")
        explanations.append(
            {
                "strategy_id": strategy_id,
                "strategy_positioning": STRATEGY_POSITIONING.get(strategy_id, "Baseline strategy signal used for day1 virtual forward dry-run."),
                "input_data_date": signal.get("signal_date"),
                "target_weights_summary": signal.get("target_weights", {}),
                "cash_weight": signal.get("cash_weight"),
                "main_signal_reasons": {
                    "diagnostics": signal.get("diagnostics", {}),
                    "warnings": signal.get("warnings", []),
                    "no_future_price_data": signal.get("no_future_price_data"),
                    "no_future_risk_proxy": signal.get("no_future_risk_proxy"),
                },
                "uses_ml": bool(signal.get("uses_ml_shadow")),
                "uses_llm": bool(signal.get("uses_llm")),
                "uses_rl": bool(signal.get("uses_rl")),
                "promotion_authorized": bool(signal.get("uses_promotion_outputs")),
                "strategy_effectiveness_proven": False,
            }
        )
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-STRATEGY-SIGNAL-EXPLANATION",
        "day_index": 1,
        "strategies_total": signals_payload.get("strategies_total", len(explanations)),
        "strategies_explained": len(explanations),
        "strategy_explanations": explanations,
        "boundary": {
            **report_boundary("baseline_strategies_only"),
            "baseline_strategies_only": True,
            "ml_shadow_used_as_authorization": False,
            "llm_trading_decision": False,
            "rl_used": False,
            "promotion_triggered": False,
            "strategy_effectiveness_proven": False,
        },
    }
    lines = [
        f"- strategies_total: {payload['strategies_total']}",
        f"- strategies_explained: {payload['strategies_explained']}",
        "",
        "## Strategies",
    ]
    lines.extend(f"- {item['strategy_id']}: cash_weight={item['cash_weight']} ML=false LLM=false RL=false promotion=false" for item in explanations)
    return write_report_artifact(paths, "day1_strategy_signal_explanation.json", payload, "DAY1_STRATEGY_SIGNAL_EXPLANATION.md", build_simple_markdown("Day1 Strategy Signal Explanation", lines, payload))
