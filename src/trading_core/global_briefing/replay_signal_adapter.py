"""Convert global-briefing macro bundle rows into isolated replay targets."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.isolated_replay_state import ReplaySignal


DEFAULT_CHINA_ETF_UNIVERSE = [
    "510300.SH",
    "159915.SZ",
    "588000.SH",
    "512480.SH",
    "512660.SH",
    "512880.SH",
    "2800.HK",
    "3033.HK",
]
KNOWN_SIGNAL_FIELDS = {"risk_on", "liquidity", "policy_support"}
ADAPTER_ID = "global_briefing_isolated_replay_adapter_v1"


def adapt_bundle_row_to_replay_signals(
    bundle_row: dict[str, Any],
    *,
    replay_id: str,
    max_symbol_weight: float = 0.15,
    max_total_weight: float = 0.50,
    universe: list[str] | None = None,
) -> tuple[list[ReplaySignal], list[str]]:
    universe = universe or DEFAULT_CHINA_ETF_UNIVERSE
    raw_signals = bundle_row.get("signals")
    replay_date = str(bundle_row.get("replay_date"))
    warnings: list[str] = []
    if not isinstance(raw_signals, dict) or not raw_signals:
        warnings.append(f"{replay_date}: missing macro signals; cash-only replay target")
        return [], warnings

    unknown = sorted(set(raw_signals) - KNOWN_SIGNAL_FIELDS)
    if unknown:
        warnings.append(f"{replay_date}: unknown signal fields ignored: {unknown}")

    weights: dict[str, float] = {}
    risk_on = _positive_number(raw_signals.get("risk_on"))
    liquidity = _positive_number(raw_signals.get("liquidity"))
    policy_support = _positive_number(raw_signals.get("policy_support"))

    if risk_on > 0 or policy_support > 0:
        weights["510300.SH"] = min(max_symbol_weight, (0.20 * risk_on) + (0.15 * policy_support))
    if liquidity > 0 and "588000.SH" in universe:
        weights["588000.SH"] = min(max_symbol_weight, 0.10 * liquidity)
    if policy_support > 0 and "512880.SH" in universe:
        weights["512880.SH"] = min(max_symbol_weight, 0.05 * policy_support)

    weights = {symbol: max(0.0, weight) for symbol, weight in weights.items() if weight > 0 and symbol in universe}
    total = sum(weights.values())
    if total > max_total_weight and total > 0:
        scale = max_total_weight / total
        weights = {symbol: weight * scale for symbol, weight in weights.items()}

    signals = [
        ReplaySignal(
            replay_id=replay_id,
            replay_date=replay_date,
            symbol=symbol,
            target_weight=round(weight, 6),
            reason="macro_signal_adapter",
            source_signal_as_of_date=bundle_row.get("selected_signal_as_of_date"),
            source_signal_generated_at=bundle_row.get("selected_signal_generated_at"),
        )
        for symbol, weight in sorted(weights.items())
        if weight > 0
    ]
    if not signals:
        warnings.append(f"{replay_date}: macro signals produced no positive target; cash-only replay target")
    return signals, warnings


def _positive_number(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, min(float(value), 1.0))
