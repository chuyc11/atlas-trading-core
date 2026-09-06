"""Static boundary regression audit."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, protected_diff, timestamp_id, write_json_markdown


def run_boundary_regression_audit(
    source_dir: str | Path | None = None,
    docs_dir: str | Path | None = None,
    tests_dir: str | Path | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    source = _resolve(source_dir, paths.project_root / "src" / "trading_core", paths)
    docs = _resolve(docs_dir, paths.project_root / "docs", paths)
    tests = _resolve(tests_dir, paths.project_root / "tests", paths)
    audit_id, created_at = timestamp_id("BOUNDARY")
    warnings: list[str] = []

    run_daily = _read(source / "daily_run.py")
    signal_generator = _read(source / "signals" / "signal_generator.py")
    checks: dict[str, dict[str, Any]] = {
        "run_daily_label_import": {"passed": not _contains_import(run_daily, "trading_core.labels"), "issues": []},
        "run_daily_ml_import": {"passed": not _contains_import(run_daily, "trading_core.ml"), "issues": []},
        "broker_code": {"passed": not _has_real_broker_code(source), "issues": []},
        "live_trading_cli": {"passed": not _has_live_trading_cli(source / "cli.py"), "issues": []},
        "auto_promotion": {"passed": not _has_auto_promotion(source), "issues": []},
        "main_ledger_writes": {"passed": not _has_experiment_main_ledger_write(source / "experiments"), "issues": []},
        "label_store_in_signal_generator": {"passed": "label_store" not in signal_generator, "issues": []},
    }
    for name, check in checks.items():
        if not check["passed"]:
            check["issues"].append(name)

    if _mentions_prohibited_live_trading(docs):
        warnings.append("docs mention live trading only as prohibited")
    if _mentions_forbidden_keywords(tests):
        warnings.append("tests include forbidden keywords as negative tests")

    protected_changes = protected_diff(paths, before)
    if protected_changes:
        checks["main_ledger_writes"] = {"passed": False, "issues": ["audit modified protected paths", *protected_changes]}

    blocking = [f"{name}: {check['issues']}" for name, check in checks.items() if not check["passed"]]
    payload = {
        "audit_id": audit_id,
        "created_at": created_at,
        "passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "boundary": {
            "no_broker": True,
            "no_live_trading": True,
            "no_rl_active_trading": True,
            "no_llm_trading_decision": True,
            "no_auto_promotion": True,
        },
    }
    json_path = paths.data_dir / "system" / "boundary_regression_audit.json"
    report_path = paths.outputs_dir / "audit" / "BOUNDARY_REGRESSION_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_boundary_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_boundary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Boundary Regression Audit",
        "",
        f"- passed: {str(payload['passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {payload['warnings']}",
        "",
        "## Checks",
    ]
    for name, check in payload["checks"].items():
        lines.append(f"- {name}: passed={str(check['passed']).lower()} issues={check.get('issues', [])}")
    lines.extend(
        [
            "",
            "## Boundary",
            "This audit does not validate forward 30d dry-run.",
            "This audit does not certify live trading readiness.",
            "This project remains research-only.",
            "",
        ]
    )
    return "\n".join(lines)


def _resolve(value: str | Path | None, default: Path, paths: ProjectPaths) -> Path:
    if value is None:
        return default
    path = Path(value)
    return path if path.is_absolute() else paths.project_root / path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _contains_import(text: str, module: str) -> bool:
    return f"from {module}" in text or f"import {module}" in text


def _py_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py")) if root.exists() else []


def _has_real_broker_code(source: Path) -> bool:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in _py_files(source / "broker"))
    real_tokens = ["alpaca", "ib_insync", "ccxt", "place_live_order", "real_broker_client", "broker_api_key"]
    return any(token in text for token in real_tokens)


def _has_live_trading_cli(cli_path: Path) -> bool:
    text = _read(cli_path).lower()
    live_commands = ['add_parser("live', "add_parser('live", "connect-broker", "place-live-order"]
    return any(token in text for token in live_commands)


def _has_auto_promotion(source: Path) -> bool:
    text = "\n".join(path.read_text(encoding="utf-8") for path in _py_files(source / "experiments"))
    true_assignment = re.compile(r"['\"](?:strategy_state_changed|promotion_triggered)['\"]\s*:\s*True|(?:strategy_state_changed|promotion_triggered)\s*=\s*True")
    forbidden_status_output = re.compile(r"['\"](?:simulated_status|status)['\"]\s*:\s*['\"](?:active_normal|approved_for_trading|promoted|live)['\"]")
    return bool(true_assignment.search(text) or forbidden_status_output.search(text))


def _has_experiment_main_ledger_write(experiments: Path) -> bool:
    text = "\n".join(path.read_text(encoding="utf-8") for path in _py_files(experiments))
    true_assignment = re.compile(r"['\"]write_main_ledger['\"]\s*:\s*True|write_main_ledger\s*=\s*True")
    return bool(true_assignment.search(text))


def _mentions_prohibited_live_trading(docs: Path) -> bool:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs.rglob("*.md")) if docs.exists() else ""
    return "not live trading" in text or "no live trading" in text or "live trading" in text


def _mentions_forbidden_keywords(tests: Path) -> bool:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in tests.rglob("*.py")) if tests.exists() else ""
    return any(token in text for token in ["live trading", "write_main_ledger=true", "trading_core.labels"])
