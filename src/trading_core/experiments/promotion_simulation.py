"""Offline promotion simulation from strategy comparison artifacts.

This module is deliberately read-only with respect to strategy state and trading
ledgers. It writes only simulation artifacts under data/experiments and
outputs/experiments.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


ALLOWED_SIMULATED_STATUSES = {
    "reject",
    "watch",
    "shadow_candidate",
    "active_small_candidate",
}
KNOWN_SOURCE_TYPES = {"parameter_sweep", "ml_shadow_leaderboard", "backtest"}
PROMOTABLE_SOURCE_TYPES = {"parameter_sweep", "backtest"}
FORBIDDEN_RECOMMENDATIONS = {
    "active",
    "active_normal",
    "live",
    "promoted",
    "approved_for_trading",
}
BOUNDARY = {
    "simulation_only": True,
    "strategy_state_changed": False,
    "write_main_ledger": False,
    "allow_active": False,
    "orders_written": False,
    "trades_written": False,
    "portfolio_written": False,
    "accounts_written": False,
    "strategy_config_changed": False,
    "promotion_gate_changed": False,
    "run_daily_called": False,
    "broker_called": False,
    "real_data_acquisition_called": False,
    "rl_used": False,
    "llm_trading_decision_used": False,
}


class PromotionSimulationInputError(ValueError):
    """Raised when a promotion simulation input path cannot be used."""


def run_promotion_simulation(
    comparison_path: str | Path,
    score_threshold: float = 5.0,
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Run a read-only promotion simulation from a strategy comparison JSON."""
    paths = paths or project_paths()
    input_path = _resolve_input_path(Path(comparison_path), paths)
    if not input_path.exists():
        raise PromotionSimulationInputError(f"comparison file not found: {comparison_path}")

    warnings: list[str] = []
    comparison = _read_comparison(input_path, warnings)
    comparison_id = _comparison_id(comparison, input_path)
    raw_items = _comparison_items(comparison, warnings)
    evaluated_items = [
        evaluate_simulation_item(item, score_threshold=score_threshold, strict=strict, warnings=warnings)
        for item in raw_items
    ]

    summary = _summary(evaluated_items)
    timestamp = datetime.now(UTC)
    file_timestamp = timestamp.strftime("%Y%m%d-%H%M%S-%f")
    payload = {
        "simulation_id": f"PROMOSIM-{timestamp:%Y%m%d-%H%M%S}",
        "created_at": timestamp.isoformat().replace("+00:00", "Z"),
        "comparison_id": comparison_id,
        "input_path": str(comparison_path),
        "score_threshold": score_threshold,
        "strict": strict,
        "items": evaluated_items,
        "summary": summary,
        "warnings": warnings,
        "boundary": BOUNDARY.copy(),
    }
    _assert_no_forbidden_statuses(payload)

    data_path = paths.data_dir / "experiments" / f"promotion_simulation-{file_timestamp}.json"
    report_path = paths.outputs_dir / "experiments" / f"PROMOTION_SIMULATION-{file_timestamp}.md"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_promotion_simulation_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(data_path), "report_path": str(report_path)}


def evaluate_simulation_item(
    item: dict[str, Any],
    score_threshold: float = 5.0,
    strict: bool = False,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate one comparison item into a simulation-only status."""
    warnings = warnings if warnings is not None else []
    metrics = _extract_metrics(item)
    source_type = _source_type(item)
    item_id = _item_id(item)
    strategy_id = _string_or_none(item.get("strategy_id"))
    model_id = _string_or_none(item.get("model_id"))
    current_recommendation = _current_recommendation(item, warnings, item_id)

    reason_codes: list[str] = []
    missing = _missing_metrics(metrics)
    status = "watch"

    if source_type not in KNOWN_SOURCE_TYPES:
        status = "reject"
        reason_codes.append("unknown_source_type")
        warnings.append(f"{item_id}: unknown source_type '{source_type}'")
    elif current_recommendation == "reject":
        status = "reject"
        reason_codes.append("rejected_by_comparison")
    elif current_recommendation == "weak":
        status = "reject"
        reason_codes.append("weak_ml_shadow_result")
    elif missing:
        reason_codes.extend(missing)
        reason_codes.append("insufficient_data")
        status = "reject" if strict else "watch"
        if strict:
            reason_codes.append("missing_required_metrics")
    else:
        excess_return = metrics["excess_return"]
        max_drawdown = metrics["max_drawdown"]
        trade_count = metrics["trade_count"]
        score = metrics.get("score")
        cost_ratio = metrics.get("cost_ratio")

        if excess_return <= 0:
            status = "reject"
            reason_codes.append("negative_excess_return")
        elif max_drawdown > 0.08:
            status = "reject"
            reason_codes.append("excessive_drawdown")
        elif trade_count < 10:
            status = "reject"
            reason_codes.append("insufficient_trade_count")
        elif (
            source_type in PROMOTABLE_SOURCE_TYPES
            and current_recommendation == "promising_shadow"
            and score is not None
            and score > score_threshold * 2
            and max_drawdown <= 0.03
            and trade_count >= 20
            and cost_ratio is not None
            and cost_ratio <= 0.005
        ):
            status = "active_small_candidate"
            reason_codes.extend(
                [
                    "strong_shadow_metrics",
                    "low_drawdown",
                    "sufficient_sample_size",
                    "cost_ratio_acceptable",
                    "simulation_only_no_state_change",
                ]
            )
        elif (
            source_type in PROMOTABLE_SOURCE_TYPES
            and current_recommendation in {"watch", "promising_shadow"}
            and score is not None
            and score > score_threshold
            and max_drawdown <= 0.05
            and trade_count >= 10
        ):
            status = "shadow_candidate"
            reason_codes.extend(
                [
                    "positive_excess_return",
                    "score_above_threshold",
                    "drawdown_acceptable",
                    "sufficient_trade_count",
                    "shadow_only_candidate",
                ]
            )
        else:
            status = "watch"
            if score is None:
                reason_codes.append("missing_score")
            elif score <= score_threshold:
                reason_codes.append("positive_but_score_insufficient")
            if max_drawdown > 0.05:
                reason_codes.append("moderate_drawdown")
            if trade_count < 20:
                reason_codes.append("requires_more_data")
            if current_recommendation == "watch":
                reason_codes.append("ml_shadow_watch" if source_type == "ml_shadow_leaderboard" else "comparison_watch")
            if source_type == "ml_shadow_leaderboard":
                reason_codes.append("requires_comparable_shadow_evidence")

    if not reason_codes:
        reason_codes.append("requires_more_data")

    result = {
        "item_id": item_id,
        "source_type": source_type,
        "strategy_id": strategy_id,
        "model_id": model_id,
        "current_recommendation": current_recommendation,
        "simulated_status": status,
        "reason_codes": _dedupe(reason_codes),
        "metrics": metrics,
    }
    _assert_allowed_item(result)
    return result


def build_promotion_simulation_markdown(payload: dict[str, Any]) -> str:
    """Build a markdown report for promotion simulation results."""
    items = payload.get("items", [])
    summary = payload.get("summary", {})
    warnings = payload.get("warnings", [])
    shadow_candidates = [item for item in items if item.get("simulated_status") == "shadow_candidate"]
    active_small_candidates = [item for item in items if item.get("simulated_status") == "active_small_candidate"]

    lines = [
        "# Promotion Simulation Report",
        "",
        "## 1. Scope",
        "",
        f"* simulation_id: {payload.get('simulation_id', '')}",
        f"* created_at: {payload.get('created_at', '')}",
        f"* comparison_id: {payload.get('comparison_id', '')}",
        f"* input_path: {payload.get('input_path', '')}",
        f"* score_threshold: {payload.get('score_threshold', '')}",
        f"* strict mode: {str(payload.get('strict', False)).lower()}",
        "",
        "## 2. Summary",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status in ["reject", "watch", "shadow_candidate", "active_small_candidate"]:
        lines.append(f"| {status} | {summary.get(status, 0)} |")

    lines.extend(
        [
            "",
            "## 3. Simulated Items",
            "",
            "| item_id | source_type | strategy_id | model_id | current_recommendation | simulated_status | excess_return | max_drawdown | trade_count | score | reason_codes |",
            "|---|---|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in items:
        metrics = item.get("metrics", {})
        lines.append(
            "| {item_id} | {source_type} | {strategy_id} | {model_id} | {current_recommendation} | {simulated_status} | {excess_return} | {max_drawdown} | {trade_count} | {score} | {reason_codes} |".format(
                item_id=_md(item.get("item_id")),
                source_type=_md(item.get("source_type")),
                strategy_id=_md(item.get("strategy_id")),
                model_id=_md(item.get("model_id")),
                current_recommendation=_md(item.get("current_recommendation")),
                simulated_status=_md(item.get("simulated_status")),
                excess_return=_md(_format_metric(metrics.get("excess_return"))),
                max_drawdown=_md(_format_metric(metrics.get("max_drawdown"))),
                trade_count=_md(_format_metric(metrics.get("trade_count"))),
                score=_md(_format_metric(metrics.get("score"))),
                reason_codes=_md(", ".join(item.get("reason_codes", []))),
            )
        )

    lines.extend(["", "## 4. Candidate Review", "", "### Shadow Candidates", ""])
    if shadow_candidates:
        for item in shadow_candidates:
            lines.append(f"* {_md(item.get('item_id'))} ({_md(item.get('strategy_id'))})")
    else:
        lines.append("No shadow candidates.")

    lines.extend(["", "### Active Small Candidates", ""])
    if active_small_candidates:
        for item in active_small_candidates:
            lines.append(f"* {_md(item.get('item_id'))} ({_md(item.get('strategy_id'))})")
    else:
        lines.append("No active small candidates.")

    lines.extend(
        [
            "",
            "These are simulated candidates only. No strategy was promoted.",
            "",
            "## 5. Warnings",
            "",
        ]
    )
    if warnings:
        for warning in warnings:
            lines.append(f"* {_md(warning)}")
    else:
        lines.append("No warnings.")

    lines.extend(
        [
            "",
            "## 6. Safety Boundary",
            "",
            "* This is a simulation only.",
            "* No strategy state was changed.",
            "* No active strategy was promoted.",
            "* No active_normal status was produced.",
            "* No live status was produced.",
            "* No orders were written.",
            "* No trades were written.",
            "* No portfolio was written.",
            "* This is not an admission gate.",
            "* This report is offline research only.",
            "",
        ]
    )
    return "\n".join(lines)


def _resolve_input_path(path: Path, paths: ProjectPaths) -> Path:
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _read_comparison(path: Path, warnings: list[str]) -> dict[str, Any] | list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PromotionSimulationInputError(f"invalid comparison JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, (dict, list)):
        warnings.append("comparison JSON root is not an object or list; treating as empty")
        return {}
    return payload


def _comparison_id(payload: dict[str, Any] | list[Any], path: Path) -> str:
    if isinstance(payload, dict):
        for key in ["comparison_id", "id"]:
            value = payload.get(key)
            if value:
                return str(value)
    return path.stem.removeprefix("strategy_comparison-")


def _comparison_items(payload: dict[str, Any] | list[Any], warnings: list[str]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    for key in ["items", "comparisons", "results", "strategies"]:
        value = payload.get(key)
        if isinstance(value, list):
            skipped = len([item for item in value if not isinstance(item, dict)])
            if skipped:
                warnings.append(f"{skipped} non-object comparison items skipped")
            return [item for item in value if isinstance(item, dict)]
    warnings.append("comparison JSON has no items")
    return []


def _source_type(item: dict[str, Any]) -> str:
    value = item.get("source_type") or item.get("source")
    if value:
        normalized = str(value).strip().lower()
        aliases = {
            "ml_shadow": "ml_shadow_leaderboard",
            "shadow_leaderboard": "ml_shadow_leaderboard",
            "strategy_results": "backtest",
            "backtest_strategy_results": "backtest",
        }
        return aliases.get(normalized, normalized)
    if item.get("model_id") or item.get("shadow_recommendation"):
        return "ml_shadow_leaderboard"
    if item.get("run_id") or item.get("experiment_id"):
        return "parameter_sweep"
    if item.get("strategy_id") and any(key in item for key in ["total_return", "win_rate", "excess_return"]):
        return "backtest"
    return "unknown"


def _item_id(item: dict[str, Any]) -> str:
    for key in ["item_id", "run_id", "strategy_id", "model_id", "experiment_id", "id"]:
        value = item.get(key)
        if value:
            return str(value)
    return "unknown_item"


def _current_recommendation(item: dict[str, Any], warnings: list[str], item_id: str) -> str:
    for key in ["current_recommendation", "recommendation", "shadow_recommendation", "status_recommendation"]:
        value = item.get(key)
        if value:
            normalized = str(value).strip().lower()
            if normalized in FORBIDDEN_RECOMMENDATIONS:
                warnings.append(f"{item_id}: forbidden recommendation '{normalized}' sanitized to reject")
                return "reject"
            return normalized
    return "watch"


def _extract_metrics(item: dict[str, Any]) -> dict[str, Any]:
    source = item.get("metrics") if isinstance(item.get("metrics"), dict) else {}
    merged = {**item, **source}
    metrics = {
        "excess_return": _numeric(
            merged,
            [
                "excess_return",
                "excess_return_vs_equal_etf",
                "excess_return_vs_benchmark",
                "top_k_excess_vs_all",
            ],
        ),
        "max_drawdown": _abs_numeric(merged, ["max_drawdown", "max_dd", "drawdown"]),
        "trade_count": _int_numeric(merged, ["trade_count", "trades", "signal_count"]),
        "score": _numeric(merged, ["score", "total_score", "composite_score"]),
        "cost_ratio": _numeric(merged, ["cost_ratio", "cost_rate"]),
    }
    return metrics


def _numeric(mapping: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


def _abs_numeric(mapping: dict[str, Any], keys: list[str]) -> float | None:
    value = _numeric(mapping, keys)
    return abs(value) if value is not None else None


def _int_numeric(mapping: dict[str, Any], keys: list[str]) -> int | None:
    value = _numeric(mapping, keys)
    return int(value) if value is not None else None


def _missing_metrics(metrics: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key, reason in [
        ("excess_return", "missing_excess_return"),
        ("max_drawdown", "missing_drawdown"),
        ("trade_count", "missing_trade_count"),
    ]:
        if metrics.get(key) is None:
            missing.append(reason)
    return missing


def _summary(items: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "total_items": len(items),
        "reject": 0,
        "watch": 0,
        "shadow_candidate": 0,
        "active_small_candidate": 0,
    }
    for item in items:
        status = str(item.get("simulated_status"))
        if status in ALLOWED_SIMULATED_STATUSES:
            summary[status] += 1
    return summary


def _assert_allowed_item(item: dict[str, Any]) -> None:
    status = item.get("simulated_status")
    if status not in ALLOWED_SIMULATED_STATUSES:
        raise AssertionError(f"forbidden simulated status produced: {status}")


def _assert_no_forbidden_statuses(payload: dict[str, Any]) -> None:
    for item in payload.get("items", []):
        status = item.get("simulated_status")
        if status not in ALLOWED_SIMULATED_STATUSES:
            raise AssertionError(f"forbidden simulated status produced: {status}")


def _dedupe(values: list[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        if value not in output:
            output.append(value)
    return output


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")
