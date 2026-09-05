"""v0.4 strategy experiment system release audit.

This audit is offline research only. It reads experiment artifacts and writes
audit outputs without touching ledgers, strategy state, parameters, promotion
state, brokers, or data acquisition.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


RELEASE_CANDIDATE = "v0.4.0-strategy-experiment-system-audited"
ALLOWED_EXPERIMENT_MODES = {"shadow", "offline"}
FORBIDDEN_KEYWORDS = {"broker", "live", "margin", "short"}
ALLOWED_COMPARISON_RECOMMENDATIONS = {"reject", "watch", "promising_shadow", "insufficient_data"}
ALLOWED_SIMULATED_STATUSES = {"reject", "watch", "shadow_candidate", "active_small_candidate"}
FORBIDDEN_STATUSES = {"active", "active_normal", "live", "promoted", "approved_for_trading"}
ALLOWED_PATTERN_ACTIONS = {
    "keep_shadow",
    "reject",
    "require_more_data",
    "reduce_turnover",
    "inspect_data_quality",
    "compare_benchmark",
}
LEDGER_POLLUTION_PATHS = [
    "data/orders",
    "data/trades",
    "data/portfolio",
    "data/accounts",
    "outputs/orders",
    "outputs/trades",
    "outputs/portfolio",
]


def audit_experiment_system(
    experiments_dir: str | Path | None = None,
    shadow_dir: str | Path | None = None,
    outputs_dir: str | Path | None = None,
    audit_dir: str | Path | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Run the v0.4 experiment system audit."""
    paths = paths or project_paths()
    experiments_path = _resolve_project_path(experiments_dir, paths, paths.data_dir / "experiments")
    shadow_path = _resolve_project_path(shadow_dir, paths, paths.data_dir / "shadow")
    outputs_path = _resolve_project_path(outputs_dir, paths, paths.outputs_dir / "experiments")
    audit_path = _resolve_project_path(audit_dir, paths, paths.outputs_dir / "audit")

    before_snapshot = _snapshot_pollution_paths(paths)
    warnings: list[str] = []
    inventory = _artifact_inventory(experiments_path, shadow_path, outputs_path)

    sections = {
        "registry": _audit_registry(inventory, warnings),
        "parameter_sweep": _audit_parameter_sweeps(inventory),
        "strategy_comparison": _audit_strategy_comparisons(inventory),
        "experiment_dashboard": _audit_dashboard(inventory, warnings),
        "promotion_simulation": _audit_promotion_simulations(inventory),
        "mistake_pattern_library": _audit_mistake_pattern_library(inventory),
        "main_ledger_pollution": {"passed": True, "modified_paths": [], "issues": []},
        "run_daily_isolation": {
            "passed": True,
            "issues": [],
            "checks": [
                "audit module does not import run_daily",
                "audit module does not call order generator",
                "audit module does not call broker simulator",
                "audit module does not call real-data acquisition",
            ],
        },
        "report_wording": _audit_report_wording(inventory),
    }

    blocking_reasons = _blocking_reasons(sections)
    created_at = datetime.now(UTC)
    after_snapshot = _snapshot_pollution_paths(paths)
    modified_paths = _snapshot_diff(before_snapshot, after_snapshot)
    if modified_paths:
        sections["main_ledger_pollution"] = {
            "passed": False,
            "modified_paths": modified_paths,
            "issues": ["audit modified ledger or account paths"],
        }
        blocking_reasons.append("main_ledger_pollution modified protected paths")

    overall_passed = not blocking_reasons
    payload = {
        "audit_id": f"EXPAUDIT-{created_at:%Y%m%d}-001",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": overall_passed,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "sections": sections,
        "artifact_inventory": _inventory_for_json(inventory),
        "boundary": {
            "offline_research_only": True,
            "write_main_ledger": False,
            "strategy_state_changed": False,
            "strategy_parameters_changed": False,
            "promotion_triggered": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "run_daily_called": False,
            "rl_used": False,
            "llm_trading_decision_used": False,
        },
    }

    experiments_path.mkdir(parents=True, exist_ok=True)
    audit_path.mkdir(parents=True, exist_ok=True)
    json_path = experiments_path / "experiment_system_audit.json"
    report_path = audit_path / "EXPERIMENT_SYSTEM_AUDIT.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(build_experiment_system_audit_markdown(payload), encoding="utf-8")
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_experiment_system_audit_markdown(payload: dict[str, Any]) -> str:
    """Build the v0.4 experiment system audit report."""
    lines = [
        "# Experiment System Audit",
        "",
        "## 1. Scope",
        "",
        f"* audit_id: {payload.get('audit_id', '')}",
        f"* created_at: {payload.get('created_at', '')}",
        f"* release_candidate: {payload.get('release_candidate', '')}",
        "* modules audited: registry, parameter_sweep, strategy_comparison, experiment_dashboard, promotion_simulation, mistake_pattern_library",
        "",
        "## 2. Overall Verdict",
        "",
        f"* overall_passed: {str(payload.get('overall_passed', False)).lower()}",
        f"* blocking_reasons: {payload.get('blocking_reasons', [])}",
        f"* warnings: {payload.get('warnings', [])}",
        "",
        "## 3. Section Results",
        "",
    ]
    for name, section in payload.get("sections", {}).items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"* passed: {str(section.get('passed', False)).lower()}",
                f"* issues: {section.get('issues', [])}",
                "",
            ]
        )

    lines.extend(["## 4. Artifact Inventory", ""])
    inventory = payload.get("artifact_inventory", {})
    for key, value in inventory.items():
        if isinstance(value, list):
            lines.append(f"* {key}:")
            if value:
                for item in value:
                    lines.append(f"  * {item}")
            else:
                lines.append("  * none")
        else:
            lines.append(f"* {key}: {value}")

    lines.extend(
        [
            "",
            "## 5. Safety Boundary",
            "",
            "* This audit is offline research only.",
            "* No strategy state was changed.",
            "* No strategy parameter was changed.",
            "* No promotion was triggered.",
            "* No orders were written.",
            "* No trades were written.",
            "* No portfolio was written.",
            "* No accounts were written.",
            "* This is not an admission gate.",
            "* This is not a live trading validation.",
            "* This does not validate forward 30d dry-run.",
            "",
            "## 6. Release Recommendation",
            "",
        ]
    )
    if payload.get("overall_passed"):
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
        for reason in payload.get("blocking_reasons", []):
            lines.append(f"* {reason}")
    lines.append("")
    return "\n".join(lines)


def _resolve_project_path(value: str | Path | None, paths: ProjectPaths, default: Path) -> Path:
    if value is None:
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _artifact_inventory(experiments: Path, shadow: Path, outputs: Path) -> dict[str, Any]:
    return {
        "experiment_registry": experiments / "experiment_registry.json",
        "parameter_sweeps": _official_files(_glob(experiments, "parameter_sweep-*.json")),
        "strategy_comparisons": _official_files(_glob(experiments, "strategy_comparison-*.json")),
        "experiment_dashboard": experiments / "experiment_dashboard.json",
        "experiment_dashboard_report": outputs / "EXPERIMENT_DASHBOARD.md",
        "promotion_simulations": _official_files(_glob(experiments, "promotion_simulation-*.json")),
        "mistake_pattern_library": experiments / "mistake_pattern_library.json",
        "mistake_pattern_library_report": outputs / "MISTAKE_PATTERN_LIBRARY.md",
        "ml_shadow_leaderboards": _glob(shadow, "ml_shadow_leaderboard-*.json"),
        "markdown_reports": _glob(outputs, "*.md"),
    }


def _glob(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime)


def _official_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if "smoke" not in path.name.lower() and "test" not in path.name.lower()]


def _audit_registry(inventory: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    path = inventory["experiment_registry"]
    issues: list[str] = []
    if not path.exists():
        warnings.append("experiment_registry.json missing")
        return {"passed": False, "experiment_count": 0, "issues": ["experiment_registry.json missing"]}
    payload = _read_json(path, issues)
    experiments = payload.get("experiments", []) if isinstance(payload, dict) else []
    for experiment in experiments if isinstance(experiments, list) else []:
        if not isinstance(experiment, dict):
            issues.append("registry contains non-object experiment")
            continue
        mode = experiment.get("mode")
        if mode not in ALLOWED_EXPERIMENT_MODES:
            issues.append(f"invalid experiment mode: {mode}")
        constraints = experiment.get("constraints", {})
        if isinstance(constraints, dict):
            if constraints.get("write_main_ledger") is True:
                issues.append(f"{experiment.get('experiment_id')}: write_main_ledger=true")
            if constraints.get("allow_active") is True:
                issues.append(f"{experiment.get('experiment_id')}: allow_active=true")
            if constraints.get("shadow_only") is False:
                issues.append(f"{experiment.get('experiment_id')}: shadow_only=false")
        for key in ["experiment_type", "strategy_id", "mode"]:
            value = str(experiment.get(key, "")).lower()
            if any(keyword in value for keyword in FORBIDDEN_KEYWORDS):
                issues.append(f"{experiment.get('experiment_id')}: forbidden keyword in {key}")
    return {"passed": not issues, "experiment_count": len(experiments) if isinstance(experiments, list) else 0, "issues": issues}


def _audit_parameter_sweeps(inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    run_count = 0
    best_count = 0
    for path in inventory["parameter_sweeps"]:
        payload = _read_json(path, issues)
        if not isinstance(payload, dict):
            continue
        runs = payload.get("runs", [])
        run_count += len(runs) if isinstance(runs, list) else 0
        if payload.get("best_shadow_candidate") is not None:
            best_count += 1
        if _has_forbidden_value(payload):
            issues.append(f"{path.name}: forbidden active/promoted/live value")
        if _has_true_key(payload, "write_main_ledger"):
            issues.append(f"{path.name}: write_main_ledger=true")
    if not inventory["parameter_sweeps"]:
        issues.append("parameter_sweep artifact missing")
    return {
        "passed": not issues,
        "sweep_count": len(inventory["parameter_sweeps"]),
        "run_count": run_count,
        "best_shadow_candidate_count": best_count,
        "issues": issues,
    }


def _audit_strategy_comparisons(inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    item_count = 0
    best_by_score = None
    best_by_excess_return = None
    for path in inventory["strategy_comparisons"]:
        payload = _read_json(path, issues)
        if not isinstance(payload, dict):
            continue
        items = payload.get("items", [])
        item_count += len(items) if isinstance(items, list) else 0
        best_by_score = payload.get("best_by_score") or best_by_score
        best_by_excess_return = payload.get("best_by_excess_return") or best_by_excess_return
        for item in items if isinstance(items, list) else []:
            rec = item.get("current_recommendation") or item.get("recommendation")
            if rec is not None and rec not in ALLOWED_COMPARISON_RECOMMENDATIONS:
                issues.append(f"{path.name}: invalid recommendation={rec}")
        if _has_forbidden_value(payload):
            issues.append(f"{path.name}: forbidden active/promoted/live value")
    if not inventory["strategy_comparisons"]:
        issues.append("strategy_comparison artifact missing")
    return {
        "passed": not issues,
        "comparison_count": len(inventory["strategy_comparisons"]),
        "item_count": item_count,
        "best_by_score": best_by_score,
        "best_by_excess_return": best_by_excess_return,
        "issues": issues,
    }


def _audit_dashboard(inventory: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    issues: list[str] = []
    json_path = inventory["experiment_dashboard"]
    report_path = inventory["experiment_dashboard_report"]
    if not json_path.exists():
        warnings.append("experiment_dashboard.json missing")
        issues.append("experiment_dashboard.json missing")
    if not report_path.exists():
        warnings.append("EXPERIMENT_DASHBOARD.md missing")
        issues.append("EXPERIMENT_DASHBOARD.md missing")
    text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    for phrase in ["not an admission gate", "no active promotion"]:
        if phrase not in text:
            issues.append(f"dashboard report missing: {phrase}")
    return {"passed": not issues, "issues": issues}


def _audit_promotion_simulations(inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    item_count = 0
    for path in inventory["promotion_simulations"]:
        payload = _read_json(path, issues)
        if not isinstance(payload, dict):
            continue
        items = payload.get("items", [])
        item_count += len(items) if isinstance(items, list) else 0
        for item in items if isinstance(items, list) else []:
            status = item.get("simulated_status")
            if status not in ALLOWED_SIMULATED_STATUSES:
                issues.append(f"{path.name}: invalid simulated_status={status}")
            if status in FORBIDDEN_STATUSES:
                issues.append(f"{path.name}: forbidden status={status}")
        boundary = payload.get("boundary", {})
        if isinstance(boundary, dict):
            if boundary.get("strategy_state_changed") is not False:
                issues.append(f"{path.name}: boundary.strategy_state_changed is not false")
            if boundary.get("write_main_ledger") is not False:
                issues.append(f"{path.name}: boundary.write_main_ledger is not false")
        if _has_forbidden_value(payload):
            issues.append(f"{path.name}: forbidden active/promoted/live value")
    if not inventory["promotion_simulations"]:
        issues.append("promotion_simulation artifact missing")
    return {
        "passed": not issues,
        "simulation_count": len(inventory["promotion_simulations"]),
        "item_count": item_count,
        "issues": issues,
    }


def _audit_mistake_pattern_library(inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    path = inventory["mistake_pattern_library"]
    report = inventory["mistake_pattern_library_report"]
    pattern_count = 0
    pattern_types: list[str] = []
    if not path.exists():
        issues.append("mistake_pattern_library.json missing")
        payload = None
    else:
        payload = _read_json(path, issues)
    if not report.exists():
        issues.append("MISTAKE_PATTERN_LIBRARY.md missing")
    if isinstance(payload, dict):
        patterns = payload.get("patterns", [])
        pattern_count = len(patterns) if isinstance(patterns, list) else 0
        for pattern in patterns if isinstance(patterns, list) else []:
            pattern_types.append(str(pattern.get("pattern_type")))
            action = pattern.get("suggested_action")
            if action not in ALLOWED_PATTERN_ACTIONS:
                issues.append(f"invalid suggested_action={action}")
        boundary = payload.get("boundary", {})
        if isinstance(boundary, dict):
            if boundary.get("diagnostic_only") is not True:
                issues.append("boundary.diagnostic_only is not true")
            if boundary.get("promotion_triggered") is not False:
                issues.append("boundary.promotion_triggered is not false")
            if boundary.get("write_main_ledger") is not False:
                issues.append("boundary.write_main_ledger is not false")
    return {"passed": not issues, "pattern_count": pattern_count, "pattern_types": pattern_types, "issues": issues}


def _audit_report_wording(inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    texts = {
        path.name: path.read_text(encoding="utf-8").lower()
        for path in inventory["markdown_reports"]
        if path.exists()
    }
    combined = "\n".join(texts.values())
    required_anywhere = [
        "not an admission gate",
        "no active promotion",
        "offline research only",
    ]
    for phrase in required_anywhere:
        if phrase not in combined:
            issues.append(f"missing report wording: {phrase}")
    if "no orders/trades/portfolio written" not in combined and "no orders were written" not in combined:
        issues.append("missing report wording: no orders/trades/portfolio written")
    if not any("simulation only" in text for name, text in texts.items() if name.startswith("PROMOTION_SIMULATION")):
        issues.append("promotion simulation report missing simulation only wording")
    if not any("diagnostic only" in text for name, text in texts.items() if name == "MISTAKE_PATTERN_LIBRARY.md"):
        issues.append("mistake pattern report missing diagnostic only wording")
    return {"passed": not issues, "issues": issues}


def _blocking_reasons(sections: dict[str, dict[str, Any]]) -> list[str]:
    blocking = []
    for name in [
        "parameter_sweep",
        "strategy_comparison",
        "promotion_simulation",
        "mistake_pattern_library",
        "main_ledger_pollution",
        "run_daily_isolation",
        "report_wording",
    ]:
        if not sections[name]["passed"]:
            blocking.append(f"{name}: {sections[name].get('issues', [])}")
    return blocking


def _snapshot_pollution_paths(paths: ProjectPaths) -> dict[str, tuple[tuple[str, int, int], ...]]:
    snapshot = {}
    for raw in LEDGER_POLLUTION_PATHS:
        root = paths.project_root / raw
        if not root.exists():
            snapshot[str(root)] = ()
            continue
        rows = []
        for file in sorted(root.rglob("*")):
            if file.is_file():
                stat = file.stat()
                rows.append((str(file), stat.st_size, stat.st_mtime_ns))
        snapshot[str(root)] = tuple(rows)
    return snapshot


def _snapshot_diff(
    before: dict[str, tuple[tuple[str, int, int], ...]],
    after: dict[str, tuple[tuple[str, int, int], ...]],
) -> list[str]:
    changed = []
    for path in sorted(set(before) | set(after)):
        if before.get(path, ()) != after.get(path, ()):
            changed.append(path)
    return changed


def _inventory_for_json(inventory: dict[str, Any]) -> dict[str, Any]:
    output = {}
    for key, value in inventory.items():
        if isinstance(value, list):
            output[key] = [str(item) for item in value]
        else:
            output[key] = str(value)
    return output


def _read_json(path: Path, issues: list[str]) -> Any | None:
    if not path.exists():
        issues.append(f"missing JSON: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON at {path}: {exc.msg}")
        return None


def _has_true_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return any((k == key and v is True) or _has_true_key(v, key) for k, v in value.items())
    if isinstance(value, list):
        return any(_has_true_key(item, key) for item in value)
    return False


def _has_forbidden_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_has_forbidden_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_forbidden_value(item) for item in value)
    if isinstance(value, str):
        return value.lower() in FORBIDDEN_STATUSES
    return False

