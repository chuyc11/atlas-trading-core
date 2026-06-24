"""Read-only release audit for the v0.4 experiment system."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


REQUIRED_BOUNDARY_PHRASES = {
    "PARAMETER_SWEEP": [
        "not an admission gate",
        "no orders/trades/portfolio written",
    ],
    "STRATEGY_COMPARISON": [
        "not an admission gate",
        "no orders/trades/portfolio/accounts written",
        "no active promotion",
    ],
    "EXPERIMENT_DASHBOARD": [
        "not an admission gate",
        "dashboard is read-only",
        "no active promotion",
        "no orders/trades/portfolio writes",
    ],
    "PROMOTION_SIMULATION": [
        "This is a simulation only.",
        "No strategy state was changed.",
        "No active strategy was promoted.",
        "This is not an admission gate.",
    ],
    "MISTAKE_PATTERN_LIBRARY": [
        "This pattern library is diagnostic only.",
        "No strategy was modified.",
        "No parameter was modified.",
        "No promotion was triggered.",
        "This is not an admission gate.",
    ],
}


def audit_experiment_system(paths: ProjectPaths | None = None) -> dict[str, Any]:
    """Audit v0.4 experiment artifacts and write read-only audit outputs."""
    paths = paths or project_paths()
    created_at = datetime.now(UTC)
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []

    data_experiments = paths.data_dir / "experiments"
    outputs_experiments = paths.outputs_dir / "experiments"
    shadow_dir = paths.data_dir / "shadow"

    registry_path = data_experiments / "experiment_registry.json"
    dashboard_path = data_experiments / "experiment_dashboard.json"
    mistake_path = data_experiments / "mistake_pattern_library.json"
    sweeps = _official_files(_sorted_files(data_experiments, "parameter_sweep-*.json"))
    official_comparisons = [
        path for path in _sorted_files(data_experiments, "strategy_comparison-*.json")
        if _is_official_artifact(path)
    ]
    simulations = _official_files(_sorted_files(data_experiments, "promotion_simulation-*.json"))
    ml_leaderboards = _sorted_files(shadow_dir, "ml_shadow_leaderboard-*.json")

    registry = _read_json(registry_path, checks, "experiment_registry_json_valid")
    dashboard = _read_json(dashboard_path, checks, "experiment_dashboard_json_valid")
    mistake_library = _read_json(mistake_path, checks, "mistake_pattern_library_json_valid")

    _check_exists(registry_path, checks, "experiment_registry_exists")
    _check_nonempty(sweeps, checks, "parameter_sweep_exists")
    _check_nonempty(official_comparisons, checks, "strategy_comparison_exists")
    _check_exists(dashboard_path, checks, "experiment_dashboard_exists")
    _check_nonempty(simulations, checks, "promotion_simulation_exists")
    _check_exists(mistake_path, checks, "mistake_pattern_library_exists")
    _check_nonempty(ml_leaderboards, checks, "ml_shadow_leaderboard_exists")

    if registry and sweeps:
        registered = {
            str(item.get("experiment_id"))
            for item in registry.get("experiments", [])
            if isinstance(item, dict)
        }
        sweep_ids = set()
        for sweep in sweeps:
            payload = _safe_read_json(sweep, warnings)
            if isinstance(payload, dict) and payload.get("experiment_id"):
                sweep_ids.add(str(payload["experiment_id"]))
        missing = sorted(sweep_ids - registered)
        _add_check(
            checks,
            "registry_references_parameter_sweeps",
            not missing,
            {"registered": sorted(registered), "missing_sweep_ids": missing},
        )

    latest_comparison = official_comparisons[-1] if official_comparisons else None
    latest_simulation = simulations[-1] if simulations else None
    if latest_simulation and latest_comparison:
        simulation = _safe_read_json(latest_simulation, warnings)
        expected = str(latest_comparison.resolve())
        actual = str(_resolve_artifact_path(str(simulation.get("input_path", "")), paths).resolve()) if isinstance(simulation, dict) else ""
        _add_check(
            checks,
            "promotion_simulation_references_latest_comparison",
            actual == expected,
            {"expected": expected, "actual": actual},
        )

    if latest_comparison and sweeps and ml_leaderboards:
        comparison = _safe_read_json(latest_comparison, warnings)
        inputs = [
            str(_resolve_artifact_path(value, paths).resolve())
            for value in comparison.get("input_paths", [])
        ] if isinstance(comparison, dict) else []
        expected_inputs = {str(sweeps[0].resolve()), str(ml_leaderboards[0].resolve())}
        _add_check(
            checks,
            "strategy_comparison_references_inputs",
            expected_inputs.issubset(set(inputs)),
            {"expected_subset": sorted(expected_inputs), "actual": sorted(inputs)},
        )

    if dashboard:
        _add_check(
            checks,
            "dashboard_contains_core_artifacts",
            dashboard.get("registry", {}).get("experiment_count", 0) >= 1
            and len(dashboard.get("parameter_sweeps", [])) >= 1
            and len(dashboard.get("ml_shadow_results", [])) >= 1
            and len(dashboard.get("strategy_comparisons", [])) >= 1,
            {
                "registry_count": dashboard.get("registry", {}).get("experiment_count", 0),
                "parameter_sweeps": len(dashboard.get("parameter_sweeps", [])),
                "ml_shadow_results": len(dashboard.get("ml_shadow_results", [])),
                "strategy_comparisons": len(dashboard.get("strategy_comparisons", [])),
            },
        )

    if latest_simulation and mistake_library:
        latest_sim = str(latest_simulation.resolve())
        inputs = [
            str(_resolve_artifact_path(value, paths).resolve())
            for value in mistake_library.get("inputs", [])
        ] if isinstance(mistake_library, dict) else []
        _add_check(
            checks,
            "mistake_library_references_promotion_simulation",
            latest_sim in inputs,
            {"expected": latest_sim, "actual": inputs},
        )

    _audit_markdown_boundaries(outputs_experiments, checks)

    audit_passed = all(check["passed"] for check in checks)
    payload = {
        "audit_id": f"V04-AUDIT-{created_at:%Y%m%d-%H%M%S}",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "passed": audit_passed,
        "artifact_summary": {
            "experiment_registry": str(registry_path),
            "parameter_sweeps": [str(path) for path in sweeps],
            "strategy_comparisons": [str(path) for path in official_comparisons],
            "experiment_dashboard": str(dashboard_path),
            "promotion_simulations": [str(path) for path in simulations],
            "mistake_pattern_library": str(mistake_path),
            "ml_shadow_leaderboards": [str(path) for path in ml_leaderboards],
        },
        "checks": checks,
        "warnings": warnings,
        "boundary": {
            "audit_only": True,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "run_daily_called": False,
        },
    }

    data_path = data_experiments / "experiment_release_audit.json"
    report_path = outputs_experiments / "EXPERIMENT_RELEASE_AUDIT.md"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_experiment_release_audit_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(data_path), "report_path": str(report_path)}


def build_experiment_release_audit_markdown(payload: dict[str, Any]) -> str:
    """Build markdown for the v0.4 experiment system audit."""
    lines = [
        "# v0.4 Experiment System Release Audit",
        "",
        "## Summary",
        "",
        f"- audit_id: {payload.get('audit_id', '')}",
        f"- created_at: {payload.get('created_at', '')}",
        f"- passed: {str(payload.get('passed', False)).lower()}",
        "",
        "## Checks",
        "",
        "| check | passed | details |",
        "|---|---|---|",
    ]
    for check in payload.get("checks", []):
        lines.append(
            f"| {_md(check.get('name'))} | {str(check.get('passed')).lower()} | {_md(json.dumps(check.get('details', {}), ensure_ascii=False))} |"
        )
    lines.extend(["", "## Warnings", ""])
    if payload.get("warnings"):
        for warning in payload["warnings"]:
            lines.append(f"- {_md(warning)}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Audit Boundary",
            "",
            "- audit_only=true",
            "- write_main_ledger=false",
            "- no orders/trades/portfolio/accounts written",
            "- no strategy state changed",
            "- no promotion triggered",
            "- run-daily is not called",
            "- tag only after passed=true",
            "",
        ]
    )
    return "\n".join(lines)


def _sorted_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime)


def _official_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if _is_official_artifact(path)]


def _is_official_artifact(path: Path) -> bool:
    name = path.name.lower()
    return "smoke" not in name and "test" not in name


def _check_exists(path: Path, checks: list[dict[str, Any]], name: str) -> None:
    _add_check(checks, name, path.exists(), {"path": str(path)})


def _check_nonempty(paths: list[Path], checks: list[dict[str, Any]], name: str) -> None:
    _add_check(checks, name, bool(paths), {"count": len(paths), "paths": [str(path) for path in paths]})


def _read_json(path: Path, checks: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    payload = _safe_read_json(path, [])
    _add_check(checks, name, isinstance(payload, dict), {"path": str(path)})
    return payload if isinstance(payload, dict) else None


def _safe_read_json(path: Path, warnings: list[str]) -> Any | None:
    if not path.exists():
        warnings.append(f"missing JSON: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"invalid JSON: {path} ({exc.msg})")
    return None


def _audit_markdown_boundaries(outputs_dir: Path, checks: list[dict[str, Any]]) -> None:
    for prefix, phrases in REQUIRED_BOUNDARY_PHRASES.items():
        reports = _sorted_files(outputs_dir, f"{prefix}*.md")
        if not reports:
            _add_check(checks, f"{prefix.lower()}_markdown_exists", False, {"reports": []})
            continue
        report = reports[-1]
        text = report.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        _add_check(
            checks,
            f"{prefix.lower()}_boundary_phrases",
            not missing,
            {"report": str(report), "missing": missing},
        )


def _resolve_artifact_path(value: str, paths: ProjectPaths) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _add_check(checks: list[dict[str, Any]], name: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")
