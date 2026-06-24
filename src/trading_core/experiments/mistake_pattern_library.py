"""Diagnostic mistake pattern library for experiment artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import pstdev
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


PATTERN_TYPES = {
    "overfit_parameter",
    "high_turnover_low_excess",
    "low_sample_size",
    "benchmark_underperformance",
    "unstable_rank_ic",
    "cost_drag",
    "data_quality_sensitive",
}
SUGGESTED_ACTIONS = {
    "keep_shadow",
    "reject",
    "require_more_data",
    "reduce_turnover",
    "inspect_data_quality",
    "compare_benchmark",
}
SEVERITIES = {"low", "medium", "high"}
STATUSES = {"open", "monitoring", "resolved"}
BOUNDARY = {
    "diagnostic_only": True,
    "strategy_modified": False,
    "parameters_modified": False,
    "promotion_triggered": False,
    "write_main_ledger": False,
    "orders_written": False,
    "trades_written": False,
    "portfolio_written": False,
    "accounts_written": False,
    "run_daily_called": False,
    "broker_called": False,
    "real_data_acquisition_called": False,
    "rl_used": False,
    "llm_trading_decision_used": False,
}

_SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}
_QUALITY_TOKENS = ("data_quality", "missing_price", "stale_price", "fallback", "quality")


class MistakePatternLibraryInputError(ValueError):
    """Raised when pattern library inputs cannot be used."""


def update_mistake_pattern_library(
    input_paths: list[str | Path],
    min_evidence: int = 2,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Build and persist a diagnostic mistake pattern library."""
    paths = paths or project_paths()
    if not input_paths:
        raise MistakePatternLibraryInputError("at least one input artifact is required")
    if min_evidence < 1:
        raise MistakePatternLibraryInputError("min_evidence must be >= 1")

    warnings: list[str] = []
    buckets: dict[str, list[dict[str, Any]]] = {pattern_type: [] for pattern_type in PATTERN_TYPES}
    normalized_inputs: list[str] = []

    for value in input_paths:
        input_path = _resolve_input_path(Path(value), paths)
        normalized_inputs.append(str(value))
        if not input_path.exists():
            raise MistakePatternLibraryInputError(f"input artifact not found: {value}")
        payload = _read_json_or_warn(input_path, warnings)
        if payload is None:
            continue
        _collect_from_payload(payload, input_path, buckets, warnings)

    pattern_specs = _build_pattern_specs(buckets, min_evidence, warnings)
    patterns = _finalize_patterns(pattern_specs)
    timestamp = datetime.now(UTC)
    payload = {
        "library_id": f"MISTAKE-LIB-{timestamp:%Y%m%d}-001",
        "created_at": timestamp.isoformat().replace("+00:00", "Z"),
        "inputs": normalized_inputs,
        "min_evidence": min_evidence,
        "patterns": patterns,
        "warnings": warnings,
        "boundary": BOUNDARY.copy(),
    }
    _assert_allowed_payload(payload)

    data_path = paths.data_dir / "experiments" / "mistake_pattern_library.json"
    report_path = paths.outputs_dir / "experiments" / "MISTAKE_PATTERN_LIBRARY.md"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_mistake_pattern_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(data_path), "report_path": str(report_path)}


def build_mistake_pattern_markdown(payload: dict[str, Any]) -> str:
    """Build markdown for a mistake pattern library payload."""
    patterns = payload.get("patterns", [])
    warnings = payload.get("warnings", [])
    lines = [
        "# Mistake Pattern Library",
        "",
        "## 1. Scope",
        "",
        f"* library_id: {payload.get('library_id', '')}",
        f"* created_at: {payload.get('created_at', '')}",
        f"* input count: {len(payload.get('inputs', []))}",
        f"* pattern count: {len(patterns)}",
        f"* min_evidence: {payload.get('min_evidence', '')}",
        "",
        "## 2. Summary",
        "",
    ]
    if not patterns:
        lines.append("No formal mistake patterns detected.")
    else:
        lines.extend(
            [
                "| pattern_type | evidence_count | severity | affected_strategies | affected_experiments | affected_models | suggested_action | status |",
                "|---|---:|---|---|---|---|---|---|",
            ]
        )
        for pattern in patterns:
            lines.append(
                "| {pattern_type} | {evidence_count} | {severity} | {strategies} | {experiments} | {models} | {action} | {status} |".format(
                    pattern_type=_md(pattern.get("pattern_type")),
                    evidence_count=pattern.get("evidence_count", 0),
                    severity=_md(pattern.get("severity")),
                    strategies=_md(", ".join(pattern.get("affected_strategies", []))),
                    experiments=_md(", ".join(pattern.get("affected_experiments", []))),
                    models=_md(", ".join(pattern.get("affected_models", []))),
                    action=_md(pattern.get("suggested_action")),
                    status=_md(pattern.get("status")),
                )
            )

    lines.extend(["", "## 3. Patterns", ""])
    if not patterns:
        lines.append("No formal mistake patterns detected.")
    else:
        for pattern in patterns:
            lines.extend(
                [
                    f"### {pattern.get('pattern_id')} - {pattern.get('pattern_type')}",
                    "",
                    f"* description: {pattern.get('description', '')}",
                    f"* severity: {pattern.get('severity', '')}",
                    f"* evidence_count: {pattern.get('evidence_count', 0)}",
                    f"* affected_strategies: {', '.join(pattern.get('affected_strategies', []))}",
                    f"* affected_experiments: {', '.join(pattern.get('affected_experiments', []))}",
                    f"* affected_models: {', '.join(pattern.get('affected_models', []))}",
                    f"* suggested_action: {pattern.get('suggested_action', '')}",
                    f"* status: {pattern.get('status', '')}",
                    "",
                    "Evidence examples",
                    "",
                    "| source_type | source_id | item_id | metric | value | reason |",
                    "|---|---|---|---|---:|---|",
                ]
            )
            for evidence in pattern.get("evidence", []):
                lines.append(
                    "| {source_type} | {source_id} | {item_id} | {metric} | {value} | {reason} |".format(
                        source_type=_md(evidence.get("source_type")),
                        source_id=_md(evidence.get("source_id")),
                        item_id=_md(evidence.get("item_id")),
                        metric=_md(evidence.get("metric")),
                        value=_md(_format_value(evidence.get("value"))),
                        reason=_md(evidence.get("reason")),
                    )
                )
            lines.append("")

    lines.extend(["## 4. Warnings", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"* {_md(warning)}")
    else:
        lines.append("No warnings.")

    lines.extend(
        [
            "",
            "## 5. Diagnostic Boundary",
            "",
            "* This pattern library is diagnostic only.",
            "* No strategy was modified.",
            "* No parameter was modified.",
            "* No promotion was triggered.",
            "* No orders were written.",
            "* No trades were written.",
            "* No portfolio was written.",
            "* No accounts were written.",
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


def _read_json_or_warn(path: Path, warnings: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"malformed input skipped: {path.name} ({exc.msg})")
    except OSError as exc:
        warnings.append(f"input skipped: {path.name} ({exc})")
    return None


def _collect_from_payload(
    payload: Any,
    path: Path,
    buckets: dict[str, list[dict[str, Any]]],
    warnings: list[str],
) -> None:
    if not isinstance(payload, dict):
        warnings.append(f"unknown input skipped: {path.name}")
        return
    if "experiment_id" in payload and isinstance(payload.get("runs"), list):
        _collect_parameter_sweep(payload, buckets)
        _collect_payload_quality(payload, "parameter_sweep", str(payload.get("experiment_id")), path.name, buckets)
        return
    if "simulation_id" in payload and isinstance(payload.get("items"), list):
        _collect_promotion_simulation(payload, buckets)
        _collect_payload_quality(payload, "promotion_simulation", str(payload.get("simulation_id")), path.name, buckets)
        return
    if "comparison_id" in payload and isinstance(payload.get("items"), list):
        _collect_strategy_comparison(payload, buckets)
        _collect_payload_quality(payload, "strategy_comparison", str(payload.get("comparison_id")), path.name, buckets)
        return
    if _looks_like_ml_shadow_leaderboard(payload):
        _collect_ml_shadow(payload, buckets)
        _collect_payload_quality(payload, "ml_shadow_leaderboard", str(payload.get("model_id", path.stem)), path.name, buckets)
        return
    warnings.append(f"unknown input skipped: {path.name}")


def _collect_parameter_sweep(payload: dict[str, Any], buckets: dict[str, list[dict[str, Any]]]) -> None:
    experiment_id = str(payload.get("experiment_id", "unknown_experiment"))
    strategy_id = _string(payload.get("strategy_id"))
    runs = [run for run in payload.get("runs", []) if isinstance(run, dict)]
    scores = [_number(run.get("score")) for run in runs]
    numeric_scores = [score for score in scores if score is not None]
    overfit_triggered = len(numeric_scores) >= 2 and max(numeric_scores) - min(numeric_scores) >= 20 and not payload.get("best_shadow_candidate")
    for run in runs:
        item_id = str(run.get("run_id", "unknown_run"))
        excess = _number(run.get("excess_return_vs_equal_etf") or run.get("excess_return"))
        turnover = _number(run.get("turnover"))
        cost_ratio = _number(run.get("cost_ratio"))
        cost_total = _number(run.get("cost_total"))
        if excess is not None and excess < 0:
            buckets["benchmark_underperformance"].append(
                _evidence("parameter_sweep", experiment_id, item_id, "excess_return_vs_equal_etf", excess, "negative excess return", strategy_id=strategy_id, experiment_id=experiment_id)
            )
        if turnover is not None and turnover >= 0.5 and excess is not None and excess <= 0:
            buckets["high_turnover_low_excess"].append(
                _evidence("parameter_sweep", experiment_id, item_id, "turnover", turnover, "high turnover with non-positive excess return", strategy_id=strategy_id, experiment_id=experiment_id)
            )
        if ((cost_ratio is not None and cost_ratio >= 0.005) or (cost_total is not None and cost_total >= 100)) and excess is not None and excess <= 0:
            buckets["cost_drag"].append(
                _evidence("parameter_sweep", experiment_id, item_id, "cost_ratio", cost_ratio if cost_ratio is not None else cost_total, "cost drag with non-positive excess return", strategy_id=strategy_id, experiment_id=experiment_id)
            )
        if overfit_triggered:
            buckets["overfit_parameter"].append(
                _evidence("parameter_sweep", experiment_id, item_id, "score", _number(run.get("score")), "score dispersion is high and no best shadow candidate was selected", strategy_id=strategy_id, experiment_id=experiment_id)
            )


def _collect_strategy_comparison(payload: dict[str, Any], buckets: dict[str, list[dict[str, Any]]]) -> None:
    comparison_id = str(payload.get("comparison_id", "unknown_comparison"))
    for item in [item for item in payload.get("items", []) if isinstance(item, dict)]:
        item_id = str(item.get("item_id") or item.get("run_id") or item.get("strategy_id") or "unknown_item")
        metrics = _metrics(item)
        strategy_id = _string(item.get("strategy_id"))
        model_id = _string(item.get("model_id"))
        source_type = str(item.get("source_type", "strategy_comparison"))
        excess = _number(metrics.get("excess_return") or metrics.get("excess_return_vs_equal_etf"))
        if excess is not None and excess < 0:
            buckets["benchmark_underperformance"].append(
                _evidence(source_type, comparison_id, item_id, "excess_return", excess, "negative excess return", strategy_id=strategy_id, model_id=model_id)
            )
        trade_count = _number(metrics.get("trade_count"))
        recommendation = str(item.get("current_recommendation") or item.get("recommendation") or "").lower()
        if (trade_count is not None and trade_count < 10) or recommendation == "insufficient_data":
            buckets["low_sample_size"].append(
                _evidence(source_type, comparison_id, item_id, "trade_count", trade_count, "insufficient sample size", strategy_id=strategy_id, model_id=model_id)
            )
        _collect_item_quality(item, source_type, comparison_id, item_id, buckets, strategy_id=strategy_id, model_id=model_id)


def _collect_promotion_simulation(payload: dict[str, Any], buckets: dict[str, list[dict[str, Any]]]) -> None:
    simulation_id = str(payload.get("simulation_id", "unknown_simulation"))
    for item in [item for item in payload.get("items", []) if isinstance(item, dict)]:
        item_id = str(item.get("item_id") or "unknown_item")
        metrics = _metrics(item)
        strategy_id = _string(item.get("strategy_id"))
        model_id = _string(item.get("model_id"))
        source_type = str(item.get("source_type", "promotion_simulation"))
        trade_count = _number(metrics.get("trade_count"))
        reason_codes = [str(value).lower() for value in item.get("reason_codes", []) if isinstance(value, str)]
        low_sample_reasons = {"insufficient_data", "missing_score", "missing_trade_count", "missing_excess_return"}
        if (
            (trade_count is not None and trade_count < 10)
            or (item.get("simulated_status") == "watch" and any(reason in low_sample_reasons for reason in reason_codes))
        ):
            buckets["low_sample_size"].append(
                _evidence(source_type, simulation_id, item_id, "trade_count", trade_count, "promotion simulation requires more data", strategy_id=strategy_id, model_id=model_id)
            )
        _collect_item_quality(item, source_type, simulation_id, item_id, buckets, strategy_id=strategy_id, model_id=model_id)


def _collect_ml_shadow(payload: dict[str, Any], buckets: dict[str, list[dict[str, Any]]]) -> None:
    model_id = str(payload.get("model_id", "unknown_model"))
    recommendation = str(payload.get("shadow_recommendation") or payload.get("recommendation") or "").lower()
    mean_rank_ic = _number(payload.get("mean_rank_ic"))
    rank_values = [
        value
        for value in (_number(value) for value in (payload.get("rank_ic_by_date") or {}).values())
        if value is not None
    ]
    unstable = recommendation in {"watch", "weak"} or (mean_rank_ic is not None and mean_rank_ic <= 0)
    if len(rank_values) >= 2 and (max(rank_values) - min(rank_values) >= 0.5 or pstdev(rank_values) >= 0.25):
        unstable = True
    if unstable:
        if rank_values:
            for key, value in (payload.get("rank_ic_by_date") or {}).items():
                number = _number(value)
                if number is not None:
                    buckets["unstable_rank_ic"].append(
                        _evidence("ml_shadow_leaderboard", model_id, str(key), "rank_ic", number, "rank IC instability", model_id=model_id)
                    )
        else:
            buckets["unstable_rank_ic"].append(
                _evidence("ml_shadow_leaderboard", model_id, model_id, "mean_rank_ic", mean_rank_ic, f"ml shadow recommendation={recommendation}", model_id=model_id)
            )


def _collect_payload_quality(
    payload: dict[str, Any],
    source_type: str,
    source_id: str,
    fallback_item_id: str,
    buckets: dict[str, list[dict[str, Any]]],
) -> None:
    for warning in payload.get("warnings", []):
        text = str(warning).lower()
        if _has_quality_token(text):
            buckets["data_quality_sensitive"].append(
                _evidence(source_type, source_id, fallback_item_id, "warning", str(warning), "input warning indicates data quality sensitivity")
            )


def _collect_item_quality(
    item: dict[str, Any],
    source_type: str,
    source_id: str,
    item_id: str,
    buckets: dict[str, list[dict[str, Any]]],
    strategy_id: str | None = None,
    model_id: str | None = None,
) -> None:
    for key in ["warnings", "reason_codes"]:
        for value in item.get(key, []):
            text = str(value).lower()
            if _has_quality_token(text):
                buckets["data_quality_sensitive"].append(
                    _evidence(source_type, source_id, item_id, key, str(value), "item reason indicates data quality sensitivity", strategy_id=strategy_id, model_id=model_id)
                )


def _build_pattern_specs(
    buckets: dict[str, list[dict[str, Any]]],
    min_evidence: int,
    warnings: list[str],
) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for pattern_type in sorted(PATTERN_TYPES):
        evidence = buckets[pattern_type]
        if not evidence:
            continue
        allow_single_ml_monitor = pattern_type == "unstable_rank_ic" and len(evidence) >= 1
        if len(evidence) < min_evidence and not allow_single_ml_monitor:
            warnings.append(f"insufficient evidence for pattern_type={pattern_type}: {len(evidence)} < {min_evidence}")
            continue
        specs.append(_pattern_spec(pattern_type, evidence))
    return specs


def _pattern_spec(pattern_type: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_count = len(evidence)
    descriptions = {
        "benchmark_underperformance": "Candidates underperformed their benchmark or EQUAL_ETF reference.",
        "high_turnover_low_excess": "High turnover did not produce positive excess return.",
        "low_sample_size": "Evidence suggests the sample size is too limited for stronger conclusions.",
        "unstable_rank_ic": "ML shadow rank IC appears weak or unstable.",
        "cost_drag": "Costs appear to drag performance while excess return is non-positive.",
        "data_quality_sensitive": "Warnings or reason codes indicate sensitivity to data quality.",
        "overfit_parameter": "Parameter scores vary widely without a durable candidate signal.",
    }
    actions = {
        "benchmark_underperformance": "compare_benchmark",
        "high_turnover_low_excess": "reduce_turnover",
        "low_sample_size": "require_more_data",
        "unstable_rank_ic": "keep_shadow",
        "cost_drag": "reduce_turnover",
        "data_quality_sensitive": "inspect_data_quality",
        "overfit_parameter": "require_more_data",
    }
    statuses = {
        "unstable_rank_ic": "monitoring",
    }
    return {
        "pattern_type": pattern_type,
        "description": descriptions[pattern_type],
        "evidence_count": evidence_count,
        "affected_strategies": _unique(e.get("strategy_id") for e in evidence),
        "affected_experiments": _unique(e.get("experiment_id") for e in evidence),
        "affected_models": _unique(e.get("model_id") for e in evidence),
        "severity": _severity(pattern_type, evidence),
        "suggested_action": actions[pattern_type],
        "status": statuses.get(pattern_type, "open"),
        "evidence": evidence[:20],
    }


def _finalize_patterns(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        specs,
        key=lambda pattern: (-_SEVERITY_RANK[pattern["severity"]], -pattern["evidence_count"], pattern["pattern_type"]),
    )
    patterns = []
    for index, pattern in enumerate(ordered, 1):
        patterns.append({"pattern_id": f"PATTERN-{index:04d}", **pattern})
    return patterns


def _severity(pattern_type: str, evidence: list[dict[str, Any]]) -> str:
    count = len(evidence)
    if pattern_type == "benchmark_underperformance":
        if count >= 10:
            return "high"
        if count >= 3:
            return "medium"
        return "low"
    if pattern_type == "high_turnover_low_excess":
        max_turnover = max((_number(e.get("value")) or 0.0) for e in evidence)
        return "high" if max_turnover >= 1.0 else "medium"
    if pattern_type in {"cost_drag", "overfit_parameter"}:
        return "high" if count >= 10 else "medium"
    if pattern_type == "unstable_rank_ic":
        return "high" if count >= 10 else "medium"
    if pattern_type == "data_quality_sensitive":
        return "medium"
    return "medium" if count >= 3 else "low"


def _looks_like_ml_shadow_leaderboard(payload: dict[str, Any]) -> bool:
    return any(key in payload for key in ["model_id", "mean_rank_ic", "prediction_count", "shadow_recommendation"])


def _metrics(item: dict[str, Any]) -> dict[str, Any]:
    metrics = item.get("metrics")
    if isinstance(metrics, dict):
        return {**item, **metrics}
    return item


def _evidence(
    source_type: str,
    source_id: str,
    item_id: str,
    metric: str,
    value: Any,
    reason: str,
    strategy_id: str | None = None,
    experiment_id: str | None = None,
    model_id: str | None = None,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_id": source_id,
        "item_id": item_id,
        "metric": metric,
        "value": value,
        "reason": reason,
        "strategy_id": strategy_id,
        "experiment_id": experiment_id,
        "model_id": model_id,
    }


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _string(value: Any) -> str | None:
    return str(value) if value is not None else None


def _unique(values: Any) -> list[str]:
    return sorted({str(value) for value in values if value not in {None, ""}})


def _has_quality_token(text: str) -> bool:
    return any(token in text for token in _QUALITY_TOKENS)


def _assert_allowed_payload(payload: dict[str, Any]) -> None:
    for pattern in payload.get("patterns", []):
        if pattern.get("pattern_type") not in PATTERN_TYPES:
            raise AssertionError(f"invalid pattern_type: {pattern.get('pattern_type')}")
        if pattern.get("suggested_action") not in SUGGESTED_ACTIONS:
            raise AssertionError(f"invalid suggested_action: {pattern.get('suggested_action')}")
        if pattern.get("severity") not in SEVERITIES:
            raise AssertionError(f"invalid severity: {pattern.get('severity')}")
        if pattern.get("status") not in STATUSES:
            raise AssertionError(f"invalid status: {pattern.get('status')}")


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")

