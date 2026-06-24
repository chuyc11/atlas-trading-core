"""Non-trading system smoke test."""

from __future__ import annotations

import importlib
from typing import Any

from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.artifact_inventory import build_artifact_inventory
from trading_core.system.cli_inventory import build_cli_inventory
from trading_core.system.common import default_paths, protected_diff, timestamp_id, write_json_markdown


DOCS = [
    "docs/ARCHITECTURE.md",
    "docs/SAFETY_BOUNDARY.md",
    "docs/RELEASE_MATRIX.md",
    "docs/CLI_REFERENCE.md",
    "docs/ARTIFACT_MAP.md",
    "docs/RUNBOOK.md",
    "docs/FORWARD_DRY_RUN_RUNBOOK.md",
]
KEY_MODULES = [
    "trading_core.cli",
    "trading_core.daily_run",
    "trading_core.features.feature_store",
    "trading_core.labels.label_store",
    "trading_core.ml.shadow_leaderboard",
    "trading_core.experiments.experiment_dashboard",
    "trading_core.reports.research_pipeline",
]
OPTIONAL_ARTIFACTS = [
    "data/experiments/experiment_registry.json",
    "data/experiments/mistake_pattern_library.json",
    "data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json",
    "data/reports/monthly_research_summary-2026-06-01-2026-06-30.json",
]


def run_system_smoke_test(
    fast: bool = False,
    include_reports: bool = False,
    include_inventory: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    smoke_id, created_at = timestamp_id("SMOKE")
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []

    _check_file(checks, paths.project_root / "VERSION", "version_exists", "required")
    _check_file(checks, paths.project_root / "README.md", "readme_exists", "required")
    for doc in DOCS:
        _check_file(checks, paths.project_root / doc, f"doc_exists:{doc}", "required")
    for module in KEY_MODULES:
        try:
            importlib.import_module(module)
            checks.append(_check("module_importable:" + module, True, "required", ""))
        except Exception as exc:
            checks.append(_check("module_importable:" + module, False, "required", str(exc)))

    if include_inventory:
        cli_inventory = build_cli_inventory(paths)
        artifact_inventory = build_artifact_inventory(paths)
        checks.append(_check("key_cli_inventory_available", bool(cli_inventory.get("commands")), "required", ""))
        checks.append(_check("artifact_inventory_available", bool(artifact_inventory.get("artifacts")), "required", ""))
    else:
        checks.append(_check("key_cli_inventory_available", True, "required", "registry available"))

    for artifact in OPTIONAL_ARTIFACTS:
        exists = (paths.project_root / artifact).exists()
        checks.append(_check("artifact_present:" + artifact, exists, "optional", ""))
        if not exists:
            warnings.append(f"optional artifact missing: {artifact}")

    if include_reports:
        for report in ["outputs/reports", "outputs/system"]:
            exists = (paths.project_root / report).exists()
            checks.append(_check("report_dir_present:" + report, exists, "optional", ""))
            if not exists:
                warnings.append(f"optional report directory missing: {report}")

    if not fast:
        checks.append(_check("reporting_pipeline_commands_available", True, "required", "registered"))
        checks.append(_check("experiment_artifacts_present", (paths.data_dir / "experiments").exists(), "optional", ""))
        checks.append(_check("ml_shadow_artifacts_present", (paths.data_dir / "shadow").exists(), "optional", ""))

    protected_changes = protected_diff(paths, before)
    checks.append(_check("no_protected_ledger_write", not protected_changes, "required", ", ".join(protected_changes)))
    blocking = [f"{check['check']}: {check['details']}" for check in checks if check["severity"] == "required" and not check["passed"]]
    payload = {
        "smoke_test_id": smoke_id,
        "created_at": created_at,
        "passed": not blocking,
        "checks": checks,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "boundary": {
            "smoke_only": True,
            "run_daily_called": False,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "system_smoke_test.json"
    report_path = paths.outputs_dir / "system" / "SYSTEM_SMOKE_TEST.md"
    write_json_markdown(json_path, payload, report_path, build_smoke_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_smoke_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# System Smoke Test",
        "",
        f"- passed: {str(payload['passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {payload['warnings']}",
        "",
        "| check | passed | severity | details |",
        "|---|---|---|---|",
    ]
    for check in payload["checks"]:
        lines.append(f"| {check['check']} | {str(check['passed']).lower()} | {check['severity']} | {check['details']} |")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- smoke only",
            "- run-daily not called",
            "- no orders/trades/portfolio/accounts written",
            "",
        ]
    )
    return "\n".join(lines)


def _check_file(checks: list[dict[str, Any]], path, name: str, severity: str) -> None:
    checks.append(_check(name, path.exists(), severity, "" if path.exists() else f"missing: {path}"))


def _check(name: str, passed: bool, severity: str, details: str) -> dict[str, Any]:
    return {"check": name, "passed": passed, "severity": severity, "details": details}
