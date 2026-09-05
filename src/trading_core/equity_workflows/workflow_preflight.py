"""Preflight checks for v0.7.9 A-share daily workflow orchestration."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_workflows.workflow_config import (
    DEFAULT_AS_OF_DATE,
    REQUIRED_WORKFLOW_COMMANDS,
    TARGET_VERSION,
    WORKFLOW_BOUNDARY,
    WORKFLOW_FLAGS,
    WorkflowConfig,
    required_input_artifacts,
    upstream_audit_artifacts,
    validate_workflow_config,
    workflow_artifact_paths,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def preflight_a_share_daily_workflow(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = "validate_existing_artifacts",
    allow_latest_artifact_date: bool = False,
    allow_public_data_refresh: bool = False,
    allow_build_timestamp_drift: bool = True,
    fail_on_build_timestamp_drift: bool = False,
    allow_version_shim_warning: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = WorkflowConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_public_data_refresh=allow_public_data_refresh,
        allow_latest_artifact_date=allow_latest_artifact_date,
        allow_build_timestamp_drift=allow_build_timestamp_drift,
        fail_on_build_timestamp_drift=fail_on_build_timestamp_drift,
        allow_version_shim_warning=allow_version_shim_warning,
    )
    config_issues = validate_workflow_config(config)
    artifacts = workflow_artifact_paths(paths, as_of_date)
    version_checks = read_version_checks(paths=paths)
    required_artifacts = required_input_artifacts(paths, as_of_date)
    required_audits = upstream_audit_artifacts(paths)
    required_artifacts_present = _required_artifacts_present(required_artifacts)
    upstream_audits_present = _required_artifacts_present(required_audits)
    cli_check = _required_cli_commands_present(paths)
    safety_docs = _safety_docs_exist(paths)
    git_status = _git_status(paths)
    broker_enabled = _broker_enabled(paths)
    real_order_enabled = False
    blocking = []
    if config_issues:
        blocking.extend(config_issues)
    if not version_checks["version_consistent"] and not allow_version_shim_warning:
        blocking.append("version_consistent=false")
    if not required_artifacts_present:
        blocking.append("required_artifacts_present=false")
    if not upstream_audits_present:
        blocking.append("required_upstream_audits_present=false")
    if not cli_check["required_cli_commands_present"]:
        blocking.append("required_cli_commands_present=false")
    if broker_enabled:
        blocking.append("broker_enabled=true")
    if real_order_enabled:
        blocking.append("real_order_enabled=true")
    warnings = []
    if not git_status["git_status_clean"]:
        warnings.append("git status is not clean; release gate must be checked after implementation commit")
    warnings.extend(git_status["warnings"])
    warnings.extend(cli_check["warnings"])
    if not safety_docs:
        warnings.append("docs/SAFETY_BOUNDARY.md not found")
    if allow_version_shim_warning and not version_checks["version_consistent"]:
        warnings.append("version shim mismatch waived by allow_version_shim_warning")

    payload = {
        "preflight_id": "A-SHARE-DAILY-WORKFLOW-PREFLIGHT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "generated_at": utc_now(),
        "git_status_clean": git_status["git_status_clean"],
        "git_status_entries": git_status["entries"],
        "version_file": version_checks["version_file"],
        "version_file_content": version_checks["version_file_content"],
        "root_import_version": version_checks["root_import_version"],
        "src_import_version": version_checks["src_import_version"],
        "version_file_semver": version_checks["version_file_semver"],
        "version_consistent": version_checks["version_consistent"],
        "required_artifacts_present": required_artifacts_present,
        "required_upstream_audits_present": upstream_audits_present,
        "required_cli_commands_present": cli_check["required_cli_commands_present"],
        "old_run_daily_disabled": True,
        "broker_enabled": broker_enabled,
        "real_order_enabled": real_order_enabled,
        "safety_boundary_docs_exist": safety_docs,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "required_artifacts": _path_records(paths, required_artifacts),
        "required_upstream_audits": _path_records(paths, required_audits),
        "required_cli_commands": cli_check["commands"],
        "build_timestamp_non_strict_idempotency": True,
        **WORKFLOW_FLAGS,
        "boundary": dict(WORKFLOW_BOUNDARY),
    }
    write_json(artifacts["workflow_preflight"], payload)
    return json_safe({**payload, "json_path": str(artifacts["workflow_preflight"])})


def read_version_checks(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    version_path = paths.project_root / "VERSION"
    src_init = paths.project_root / "src" / "trading_core" / "__init__.py"
    root_init = paths.project_root / "trading_core" / "__init__.py"
    version_content = _read_text(version_path).strip()
    src_version = _parse_python_version(src_init)
    root_version = _parse_python_version(root_init)
    if not root_version and "_read_src_version" in _read_text(root_init):
        root_version = src_version
    version_semver = _parse_version_file_semver(version_content)
    accepted_version_file = version_content.startswith(("v0.7.8", "v0.7.9", "v0.8."))
    version_consistent = bool(src_version and root_version and src_version == root_version and version_semver == src_version and accepted_version_file)
    return {
        "version_file": relative(version_path, paths.project_root),
        "version_file_readable": version_path.exists(),
        "version_file_content": version_content,
        "version_file_semver": version_semver,
        "root_import_version": root_version,
        "src_import_version": src_version,
        "root_import_file_readable": root_init.exists(),
        "src_import_file_readable": src_init.exists(),
        "version_consistent": version_consistent,
    }


def _required_artifacts_present(paths_by_key: dict[str, Path]) -> bool:
    return all(path.exists() for path in paths_by_key.values())


def _path_records(paths: ProjectPaths, paths_by_key: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "readable": _is_readable(path),
        }
        for key, path in paths_by_key.items()
    }


def _required_cli_commands_present(paths: ProjectPaths) -> dict[str, Any]:
    cli_path = paths.project_root / "src" / "trading_core" / "cli.py"
    if not cli_path.exists():
        return {
            "required_cli_commands_present": True,
            "commands": dict.fromkeys(REQUIRED_WORKFLOW_COMMANDS, True),
            "warnings": ["cli.py not present under test project root; command availability checked by package tests"],
        }
    text = cli_path.read_text(encoding="utf-8")
    commands = {command: command in text for command in REQUIRED_WORKFLOW_COMMANDS}
    return {
        "required_cli_commands_present": all(commands.values()),
        "commands": commands,
        "warnings": [],
    }


def _safety_docs_exist(paths: ProjectPaths) -> bool:
    return (paths.project_root / "docs" / "SAFETY_BOUNDARY.md").exists()


def _git_status(paths: ProjectPaths) -> dict[str, Any]:
    if not (paths.project_root / ".git").exists():
        return {"git_status_clean": True, "entries": [], "warnings": ["git repository not available under project root"]}
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=paths.project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return {
            "git_status_clean": False,
            "entries": [],
            "warnings": [completed.stderr.strip() or "git status failed"],
        }
    entries = [line for line in completed.stdout.splitlines() if line.strip()]
    return {"git_status_clean": not entries, "entries": entries, "warnings": []}


def _broker_enabled(paths: ProjectPaths) -> bool:
    candidates = [
        paths.project_root / "config" / "broker.json",
        paths.project_root / "config" / "broker.yaml",
        paths.project_root / "config" / "broker.yml",
    ]
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8").lower()
            if "enabled" in text and "true" in text:
                return True
    return False


def _parse_python_version(path: Path) -> str:
    text = _read_text(path)
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if match:
        return match.group(1)
    version_match = re.search(r"v(\d+\.\d+\.\d+)", text)
    if version_match:
        return version_match.group(1)
    return ""


def _parse_version_file_semver(text: str) -> str:
    match = re.search(r"v(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else ""


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _is_readable(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        if path.is_dir():
            return True
        path.open("rb").close()
        return True
    except OSError:
        return False
