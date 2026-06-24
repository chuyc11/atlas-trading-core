"""Read-only experiment dashboard across experiment artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


SAFETY_BOUNDARY = {
    "shadow_only": True,
    "write_main_ledger": False,
    "allow_active": False,
    "no_strategy_promotion": True,
}


def build_experiment_dashboard(
    experiments_dir: str | Path | None = None,
    shadow_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Build and persist a read-only experiment dashboard.

    The dashboard reads existing registry, parameter sweep, ML shadow leaderboard,
    and strategy comparison artifacts only. It does not write orders, trades,
    portfolios, accounts, registry state, strategy state, or promotion decisions.
    """
    paths = paths or project_paths()
    experiments_path = Path(experiments_dir) if experiments_dir else paths.data_dir / "experiments"
    shadow_path = Path(shadow_dir) if shadow_dir else paths.data_dir / "shadow"
    output_path = Path(output_dir) if output_dir else paths.outputs_dir / "experiments"

    created_at = datetime.now(UTC)
    warnings: list[str] = []

    registry = _load_registry_summary(experiments_path, warnings)
    parameter_sweeps = _load_parameter_sweeps(experiments_path, warnings)
    strategy_comparisons = _load_strategy_comparisons(experiments_path, warnings)
    ml_shadow_results = _load_ml_shadow_results(shadow_path, warnings)
    _warn_unknown_json(experiments_path, warnings)
    _warn_unknown_json(shadow_path, warnings)

    dashboard = {
        "dashboard_id": f"EXPDASH-{created_at:%Y%m%d}-001",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "registry": registry,
        "parameter_sweeps": parameter_sweeps,
        "ml_shadow_results": ml_shadow_results,
        "strategy_comparisons": strategy_comparisons,
        "safety_boundary": SAFETY_BOUNDARY.copy(),
        "warnings": warnings,
    }

    experiments_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = experiments_path / "experiment_dashboard.json"
    json_path.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False), encoding="utf-8")

    report_path = output_path / "EXPERIMENT_DASHBOARD.md"
    report_path.write_text(build_dashboard_markdown(dashboard), encoding="utf-8")

    return {
        **dashboard,
        "json_path": str(json_path),
        "report_path": str(report_path),
    }


def build_dashboard_markdown(dashboard: dict[str, Any]) -> str:
    """Build the experiment dashboard markdown report."""
    registry = dashboard.get("registry", {})
    experiments = registry.get("experiments", [])
    parameter_sweeps = dashboard.get("parameter_sweeps", [])
    ml_shadow_results = dashboard.get("ml_shadow_results", [])
    strategy_comparisons = dashboard.get("strategy_comparisons", [])
    warnings = dashboard.get("warnings", [])

    lines = [
        "# Experiment Dashboard",
        "",
        f"- dashboard_id: {dashboard.get('dashboard_id', '')}",
        f"- created_at: {dashboard.get('created_at', '')}",
        "- read-only: true",
        "",
        "## 1. Experiment Registry",
        "",
    ]

    if not experiments:
        lines.append("No registered experiments.")
    else:
        lines.extend(
            [
                "| experiment_id | strategy_id | experiment_type | status | mode |",
                "|---|---|---|---|---|",
            ]
        )
        for experiment in experiments:
            lines.append(
                "| {experiment_id} | {strategy_id} | {experiment_type} | {status} | {mode} |".format(
                    experiment_id=_md(experiment.get("experiment_id")),
                    strategy_id=_md(experiment.get("strategy_id")),
                    experiment_type=_md(experiment.get("experiment_type")),
                    status=_md(experiment.get("status")),
                    mode=_md(experiment.get("mode")),
                )
            )

    lines.extend(["", "## 2. Parameter Sweeps", ""])
    if not parameter_sweeps:
        lines.append("No parameter sweep results found.")
    else:
        lines.extend(
            [
                "| experiment_id | run count | best_shadow_candidate | best score | warnings |",
                "|---|---:|---|---:|---|",
            ]
        )
        for sweep in parameter_sweeps:
            lines.append(
                "| {experiment_id} | {run_count} | {candidate} | {score} | {warnings} |".format(
                    experiment_id=_md(sweep.get("experiment_id")),
                    run_count=sweep.get("run_count", 0),
                    candidate=_md(sweep.get("best_shadow_candidate")),
                    score=_md(_format_number(sweep.get("best_score"))),
                    warnings=_md(_join_warnings(sweep.get("warnings", []))),
                )
            )

    lines.extend(["", "## 3. ML Shadow Results", ""])
    if not ml_shadow_results:
        lines.append("No ML shadow leaderboard found.")
    else:
        lines.extend(
            [
                "| model_id | prediction_count | signal_count | mean_rank_ic | recommendation |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for result in ml_shadow_results:
            lines.append(
                "| {model_id} | {prediction_count} | {signal_count} | {rank_ic} | {recommendation} |".format(
                    model_id=_md(result.get("model_id")),
                    prediction_count=result.get("prediction_count", 0),
                    signal_count=result.get("signal_count", 0),
                    rank_ic=_md(_format_number(result.get("mean_rank_ic"))),
                    recommendation=_md(result.get("recommendation")),
                )
            )
        lines.extend(
            [
                "",
                "ML shadow recommendations such as watch, weak, promising, or promising_shadow are observation labels only.",
            ]
        )

    lines.extend(["", "## 4. Strategy Comparisons", ""])
    if not strategy_comparisons:
        lines.append("No strategy comparison found.")
    else:
        lines.extend(
            [
                "| comparison_id | item_count | best_by_score | best_by_excess_return | warnings |",
                "|---|---:|---|---|---|",
            ]
        )
        for comparison in strategy_comparisons:
            lines.append(
                "| {comparison_id} | {item_count} | {best_score} | {best_excess} | {warnings} |".format(
                    comparison_id=_md(comparison.get("comparison_id")),
                    item_count=comparison.get("item_count", 0),
                    best_score=_md(comparison.get("best_by_score")),
                    best_excess=_md(comparison.get("best_by_excess_return")),
                    warnings=_md(_join_warnings(comparison.get("warnings", []))),
                )
            )

    lines.extend(
        [
            "",
            "## 5. Safety Boundary",
            "",
            "- shadow_only=true",
            "- write_main_ledger=false",
            "- allow_active=false",
            "- no live trading",
            "- no broker",
            "- no active promotion",
            "- no main ledger writes",
            "- not an admission gate",
            "- dashboard is read-only",
            "- no orders/trades/portfolio writes",
            "- no account writes",
            "- no strategy state writes",
            "- run-daily is not called",
            "",
        ]
    )

    if warnings:
        lines.extend(["## Warnings", ""])
        for warning in warnings:
            lines.append(f"- {_md(warning)}")
        lines.append("")

    return "\n".join(lines)


def _load_registry_summary(experiments_dir: Path, warnings: list[str]) -> dict[str, Any]:
    registry_path = experiments_dir / "experiment_registry.json"
    if not registry_path.exists():
        warnings.append("experiment_registry.json not found")
        return {"experiment_count": 0, "experiments": []}

    payload = _read_json(registry_path, warnings)
    if not isinstance(payload, dict):
        warnings.append("experiment_registry.json is not an object")
        return {"experiment_count": 0, "experiments": []}

    experiments = payload.get("experiments", [])
    if not isinstance(experiments, list):
        warnings.append("experiment_registry.json experiments is not a list")
        experiments = []

    return {
        "experiment_count": len(experiments),
        "experiments": [
            {
                "experiment_id": experiment.get("experiment_id"),
                "strategy_id": experiment.get("strategy_id"),
                "experiment_type": experiment.get("experiment_type"),
                "status": experiment.get("status"),
                "mode": experiment.get("mode"),
            }
            for experiment in experiments
            if isinstance(experiment, dict)
        ],
    }


def _load_parameter_sweeps(experiments_dir: Path, warnings: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not experiments_dir.exists():
        warnings.append(f"experiments directory not found: {experiments_dir}")
        return results

    for path in sorted(experiments_dir.glob("parameter_sweep-*.json")):
        payload = _read_json(path, warnings)
        if not isinstance(payload, dict):
            warnings.append(f"{path.name} skipped: expected object")
            continue
        runs = payload.get("runs", [])
        run_count = len(runs) if isinstance(runs, list) else int(payload.get("parameter_grid_size", 0) or 0)
        best = payload.get("best_shadow_candidate")
        best_score = best.get("score") if isinstance(best, dict) else None
        results.append(
            {
                "experiment_id": payload.get("experiment_id") or path.stem.removeprefix("parameter_sweep-"),
                "run_count": run_count,
                "best_shadow_candidate": _candidate_id(best),
                "best_score": best_score,
                "warnings": _as_string_list(payload.get("warnings", [])),
            }
        )

    if not results:
        warnings.append("no parameter sweep results found")
    return results


def _load_ml_shadow_results(shadow_dir: Path, warnings: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not shadow_dir.exists():
        warnings.append(f"shadow directory not found: {shadow_dir}")
        return results

    for path in sorted(shadow_dir.glob("ml_shadow_leaderboard-*.json")):
        payload = _read_json(path, warnings)
        if not isinstance(payload, dict):
            warnings.append(f"{path.name} skipped: expected object")
            continue
        results.append(
            {
                "model_id": payload.get("model_id") or _model_id_from_leaderboard_path(path),
                "prediction_count": int(payload.get("prediction_count", 0) or 0),
                "signal_count": int(payload.get("signal_count", 0) or 0),
                "mean_rank_ic": payload.get("mean_rank_ic"),
                "recommendation": payload.get("shadow_recommendation") or payload.get("recommendation"),
            }
        )

    if not results:
        warnings.append("no ML shadow leaderboard found")
    return results


def _load_strategy_comparisons(experiments_dir: Path, warnings: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not experiments_dir.exists():
        return results

    for path in sorted(experiments_dir.glob("strategy_comparison-*.json")):
        payload = _read_json(path, warnings)
        if not isinstance(payload, (dict, list)):
            warnings.append(f"{path.name} skipped: expected object or list")
            continue
        items = _comparison_items(payload)
        results.append(
            {
                "comparison_id": _comparison_id(payload, path),
                "item_count": len(items),
                "best_by_score": _best_item_id(items, ["score", "total_score", "composite_score"]),
                "best_by_excess_return": _best_item_id(
                    items,
                    ["excess_return", "excess_return_vs_equal_etf", "excess_return_vs_benchmark"],
                ),
                "warnings": _as_string_list(payload.get("warnings", []) if isinstance(payload, dict) else []),
            }
        )

    if not results:
        warnings.append("no strategy comparison found")
    return results


def _warn_unknown_json(directory: Path, warnings: list[str]) -> None:
    if not directory.exists():
        return
    known_prefixes = (
        "experiment_registry",
        "parameter_sweep-",
        "strategy_comparison-",
        "experiment_dashboard",
        "ml_shadow_leaderboard-",
    )
    for path in sorted(directory.glob("*.json")):
        if not path.name.startswith(known_prefixes):
            warnings.append(f"unknown JSON skipped: {path.name}")


def _read_json(path: Path, warnings: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"{path.name} skipped: invalid JSON ({exc.msg})")
    except OSError as exc:
        warnings.append(f"{path.name} skipped: {exc}")
    return None


def _candidate_id(candidate: Any) -> str | None:
    if not isinstance(candidate, dict):
        return None
    for key in ["run_id", "strategy_id", "experiment_id", "model_id", "id"]:
        value = candidate.get(key)
        if value:
            return str(value)
    return None


def _comparison_items(payload: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    for key in ["items", "comparisons", "results", "strategies"]:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _comparison_id(payload: dict[str, Any] | list[Any], path: Path) -> str:
    if isinstance(payload, dict):
        for key in ["comparison_id", "id"]:
            value = payload.get(key)
            if value:
                return str(value)
    return path.stem.removeprefix("strategy_comparison-")


def _best_item_id(items: list[dict[str, Any]], score_keys: list[str]) -> str | None:
    best_item: dict[str, Any] | None = None
    best_value: float | None = None
    for item in items:
        value = _first_numeric(item, score_keys)
        if value is None:
            continue
        if best_value is None or value > best_value:
            best_value = value
            best_item = item
    if best_item is None:
        return None
    return _candidate_id(best_item) or str(best_item)


def _first_numeric(item: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


def _model_id_from_leaderboard_path(path: Path) -> str:
    stem = path.stem.removeprefix("ml_shadow_leaderboard-")
    parts = stem.split("-", 6)
    if len(parts) == 7:
        return parts[6]
    return stem


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _join_warnings(warnings: list[str]) -> str:
    return "; ".join(warnings) if warnings else ""


def _format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")

