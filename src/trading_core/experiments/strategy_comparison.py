"""Read-only strategy comparison report across experiment artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


BOUNDARY = {
    "read_only": True,
    "shadow_only": True,
    "write_main_ledger": False,
    "allow_active": False,
    "orders_written": False,
    "trades_written": False,
    "portfolio_written": False,
    "accounts_written": False,
    "strategy_state_changed": False,
    "run_daily_called": False,
    "promotion_triggered": False,
}


class StrategyComparisonInputError(ValueError):
    """Raised when strategy comparison inputs cannot be read."""


def build_strategy_comparison(
    input_paths: list[str | Path],
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Build a read-only strategy comparison from existing artifacts."""
    paths = paths or project_paths()
    if not input_paths:
        raise StrategyComparisonInputError("at least one input artifact is required")

    warnings: list[str] = []
    items: list[dict[str, Any]] = []
    resolved_inputs: list[str] = []
    for value in input_paths:
        input_path = _resolve_input_path(Path(value), paths)
        resolved_inputs.append(str(value))
        if not input_path.exists():
            raise StrategyComparisonInputError(f"input artifact not found: {value}")
        payload = _read_json(input_path)
        items.extend(_items_from_payload(payload, input_path, warnings))

    timestamp = datetime.now(UTC)
    file_timestamp = timestamp.strftime("%Y%m%d-%H%M%S-%f")
    comparison_id = f"CMP-{timestamp:%Y%m%d-%H%M%S}"
    sorted_items = sorted(
        items,
        key=lambda item: (_score_value(item), _excess_value(item)),
        reverse=True,
    )
    for rank, item in enumerate(sorted_items, 1):
        item["rank"] = rank

    payload = {
        "comparison_id": comparison_id,
        "created_at": timestamp.isoformat().replace("+00:00", "Z"),
        "input_paths": resolved_inputs,
        "item_count": len(sorted_items),
        "items": sorted_items,
        "best_by_score": _best_item_id(sorted_items, ["score"]),
        "best_by_excess_return": _best_item_id(sorted_items, ["excess_return"]),
        "warnings": warnings,
        "boundary": BOUNDARY.copy(),
    }

    data_path = paths.data_dir / "experiments" / f"strategy_comparison-{file_timestamp}.json"
    report_path = paths.outputs_dir / "experiments" / f"STRATEGY_COMPARISON-{file_timestamp}.md"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_strategy_comparison_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(data_path), "report_path": str(report_path)}


def build_strategy_comparison_markdown(payload: dict[str, Any]) -> str:
    """Build markdown for a strategy comparison payload."""
    lines = [
        "# Strategy Comparison Report",
        "",
        "## Scope",
        "",
        f"- comparison_id: {payload.get('comparison_id', '')}",
        f"- created_at: {payload.get('created_at', '')}",
        f"- item_count: {payload.get('item_count', 0)}",
        "- read-only comparison",
        "- not an admission gate",
        "- no strategy promotion",
        "",
        "## Items",
        "",
        "| rank | item_id | source_type | strategy_id | model_id | recommendation | score | excess_return | max_drawdown | trade_count | cost_ratio |",
        "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload.get("items", []):
        metrics = item.get("metrics", {})
        lines.append(
            "| {rank} | {item_id} | {source_type} | {strategy_id} | {model_id} | {recommendation} | {score} | {excess_return} | {max_drawdown} | {trade_count} | {cost_ratio} |".format(
                rank=item.get("rank", ""),
                item_id=_md(item.get("item_id")),
                source_type=_md(item.get("source_type")),
                strategy_id=_md(item.get("strategy_id")),
                model_id=_md(item.get("model_id")),
                recommendation=_md(item.get("current_recommendation")),
                score=_md(_format_metric(metrics.get("score"))),
                excess_return=_md(_format_metric(metrics.get("excess_return"))),
                max_drawdown=_md(_format_metric(metrics.get("max_drawdown"))),
                trade_count=_md(_format_metric(metrics.get("trade_count"))),
                cost_ratio=_md(_format_metric(metrics.get("cost_ratio"))),
            )
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- best_by_score: {_md(payload.get('best_by_score'))}",
            f"- best_by_excess_return: {_md(payload.get('best_by_excess_return'))}",
            "",
            "## Warnings",
            "",
        ]
    )
    warnings = payload.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {_md(warning)}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- read_only=true",
            "- shadow_only=true",
            "- write_main_ledger=false",
            "- allow_active=false",
            "- no orders/trades/portfolio/accounts written",
            "- no strategy state changed",
            "- no active promotion",
            "- not an admission gate",
            "- run-daily is not called",
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


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StrategyComparisonInputError(f"invalid JSON at {path}: {exc.msg}") from exc


def _items_from_payload(payload: Any, path: Path, warnings: list[str]) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        warnings.append(f"{path.name}: skipped non-object JSON")
        return []
    if "runs" in payload:
        return _items_from_parameter_sweep(payload, path, warnings)
    if "model_id" in payload and ("shadow_recommendation" in payload or path.name.startswith("ml_shadow_leaderboard-")):
        return [_item_from_ml_shadow_leaderboard(payload)]
    if "strategy_results" in payload or "items" in payload:
        return _items_from_backtest_like(payload, path, warnings)
    warnings.append(f"{path.name}: unknown comparison input skipped")
    return []


def _items_from_parameter_sweep(payload: dict[str, Any], path: Path, warnings: list[str]) -> list[dict[str, Any]]:
    runs = payload.get("runs", [])
    if not isinstance(runs, list):
        warnings.append(f"{path.name}: runs is not a list")
        return []
    items = []
    for run in runs:
        if not isinstance(run, dict):
            warnings.append(f"{path.name}: non-object run skipped")
            continue
        score = _number(run.get("score"))
        excess_return = _number(run.get("excess_return_vs_equal_etf") or run.get("excess_return"))
        item = {
            "item_id": str(run.get("run_id") or payload.get("experiment_id") or "unknown_run"),
            "source_type": "parameter_sweep",
            "strategy_id": run.get("strategy_id") or payload.get("strategy_id"),
            "model_id": None,
            "current_recommendation": _comparison_recommendation(score, excess_return, payload.get("best_shadow_candidate")),
            "metrics": {
                "excess_return": excess_return,
                "max_drawdown": _abs_number(run.get("max_drawdown")),
                "trade_count": _int_number(run.get("trade_count")),
                "score": score,
                "cost_ratio": _number(run.get("cost_ratio")),
            },
            "parameters": run.get("parameters", {}),
        }
        item.update(item["metrics"])
        items.append(item)
    return items


def _item_from_ml_shadow_leaderboard(payload: dict[str, Any]) -> dict[str, Any]:
    recommendation = str(payload.get("shadow_recommendation") or payload.get("recommendation") or "watch")
    metrics = {
        "excess_return": None,
        "max_drawdown": None,
        "trade_count": _int_number(payload.get("signal_count")),
        "score": _number(payload.get("mean_rank_ic")),
        "cost_ratio": None,
    }
    item = {
        "item_id": str(payload.get("model_id") or "unknown_model"),
        "source_type": "ml_shadow_leaderboard",
        "strategy_id": None,
        "model_id": payload.get("model_id"),
        "current_recommendation": recommendation,
        "metrics": metrics,
        "prediction_count": payload.get("prediction_count"),
        "signal_count": payload.get("signal_count"),
    }
    item.update(metrics)
    return item


def _items_from_backtest_like(payload: dict[str, Any], path: Path, warnings: list[str]) -> list[dict[str, Any]]:
    raw_items = payload.get("items")
    if raw_items is None:
        strategy_results = payload.get("strategy_results", {})
        if isinstance(strategy_results, dict):
            raw_items = [
                {"strategy_id": strategy_id, **value}
                for strategy_id, value in strategy_results.items()
                if isinstance(value, dict)
            ]
    if not isinstance(raw_items, list):
        warnings.append(f"{path.name}: no comparable backtest items found")
        return []
    items = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            warnings.append(f"{path.name}: non-object strategy result skipped")
            continue
        metrics_source = raw.get("admission_metrics") if isinstance(raw.get("admission_metrics"), dict) else raw
        excess_return = _number(
            metrics_source.get("excess_return")
            or metrics_source.get("excess_vs_equal_etf")
            or metrics_source.get("excess_return_vs_benchmark")
        )
        score = _number(raw.get("score") or raw.get("total_score") or excess_return)
        metrics = {
            "excess_return": excess_return,
            "max_drawdown": _abs_number(metrics_source.get("max_drawdown")),
            "trade_count": _int_number(metrics_source.get("trade_count") or metrics_source.get("trades_count")),
            "score": score,
            "cost_ratio": _number(metrics_source.get("cost_ratio")),
        }
        item = {
            "item_id": str(raw.get("item_id") or raw.get("strategy_id") or "unknown_strategy"),
            "source_type": "backtest",
            "strategy_id": raw.get("strategy_id"),
            "model_id": None,
            "current_recommendation": str(raw.get("recommendation") or "watch"),
            "metrics": metrics,
        }
        item.update(metrics)
        items.append(item)
    return items


def _comparison_recommendation(score: float | None, excess_return: float | None, best: Any) -> str:
    if excess_return is not None and excess_return <= 0:
        return "reject"
    if score is not None and score <= 0:
        return "reject"
    if isinstance(best, dict) and score is not None and score == _number(best.get("score")):
        return "promising_shadow"
    return "watch"


def _best_item_id(items: list[dict[str, Any]], keys: list[str]) -> str | None:
    best_item: dict[str, Any] | None = None
    best_value: float | None = None
    for item in items:
        for key in keys:
            value = _number(item.get("metrics", {}).get(key) if isinstance(item.get("metrics"), dict) else item.get(key))
            if value is None:
                continue
            if best_value is None or value > best_value:
                best_value = value
                best_item = item
    return str(best_item.get("item_id")) if best_item else None


def _score_value(item: dict[str, Any]) -> float:
    return _number(item.get("metrics", {}).get("score")) or float("-inf")


def _excess_value(item: dict[str, Any]) -> float:
    return _number(item.get("metrics", {}).get("excess_return")) or float("-inf")


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _abs_number(value: Any) -> float | None:
    number = _number(value)
    return abs(number) if number is not None else None


def _int_number(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


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

