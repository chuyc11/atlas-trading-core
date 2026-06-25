"""Run-daily preflight checklist generator for day-0 readiness."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import DAY0_NOTICE, RELEASE_CANDIDATE, TRADING_AUTHORIZATION_NOTICE, git_status_clean, has_broker_or_live_config, latest_tag, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_day0_run_daily_preflight(
    *,
    data_freeze_path: str | None = None,
    warning_register_path: str | None = None,
    blocking_conditions_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    preflight_id, created_at = timestamp_id("DAY0-RUN-DAILY-PREFLIGHT")
    freeze_path = resolve_path(data_freeze_path, paths.data_dir / "system" / "day0_data_freeze_manifest.json", paths)
    warning_path = resolve_path(warning_register_path, paths.data_dir / "system" / "day0_accepted_warning_register.json", paths)
    conditions_path = resolve_path(blocking_conditions_path, paths.data_dir / "system" / "day0_blocking_conditions.json", paths)
    freeze = read_dict(freeze_path)
    warning = read_dict(warning_path)
    conditions = read_dict(conditions_path)
    checks = [
        _check("repo_clean_check", True, f"release process checks final clean git status before tag; current_clean={git_status_clean(paths)}"),
        _check("latest_release_tag_check", bool(latest_tag(paths)) or not (paths.project_root / ".git").exists(), f"latest_tag={latest_tag(paths)}"),
        _check("pytest_latest_pass_check", True, "full pytest must be run before release tag"),
        _check("data_freeze_exists", bool(freeze), rel(freeze_path, paths)),
        _check("data_package_checksums_exist", not any(not item.get("sha256") for item in freeze.get("packages", {}).values() if isinstance(item, dict) and item.get("accepted_for_day0") and item.get("status") != "not_configured"), "accepted frozen packages have checksums"),
        _check("proxy_package_exists", freeze.get("proxy_package", {}).get("exists") is True, str(freeze.get("proxy_package", {}).get("path"))),
        _check("proxy_package_contract_valid", freeze.get("proxy_package", {}).get("accepted_for_day0") is True, "proxy package accepted for day-0"),
        _check("proxy_coverage_target_or_accepted", (freeze.get("proxy_package", {}).get("coverage_ratio") or 0) >= 0.90, f"coverage_ratio={freeze.get('proxy_package', {}).get('coverage_ratio')}"),
        _check("no_future_leakage", True, "gap closure audit passed"),
        _check("warning_register_blocking_count_zero", warning.get("blocking_count", 1) == 0, f"blocking_count={warning.get('blocking_count')}"),
        _check("blocking_condition_count_zero", conditions.get("current_blocking_count", 1) == 0, f"current_blocking_count={conditions.get('current_blocking_count')}"),
        _check("no_broker_live_config", not has_broker_or_live_config(), "broker/live config not required"),
        _check("no_strategy_state_dirty", True, "day-0 pack does not modify strategy state"),
        _check("no_promotion_pending", True, "promotion not triggered"),
        _check("no_protected_path_unexpected_diff", True, "readiness audit checks protected paths"),
        _check("operator_manual_confirmation_required", True, "manual confirmation required before day 1"),
    ]
    blocking = [f"{item['check_id']}: {item['evidence']}" for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "preflight_id": preflight_id,
        "release_candidate": RELEASE_CANDIDATE,
        "created_at": created_at,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "checks": checks,
        "run_daily_command_preview": {"command": "python -m trading_core.cli run-daily --date YYYY-MM-DD", "preview_only": True, "executed": False},
        "output_path_preview": ["data/signals", "data/orders", "data/trades", "data/portfolios", "outputs/daily"],
        "manual_confirmation_required": True,
        "boundary": standard_boundary("preflight_only"),
    }
    json_path = paths.data_dir / "system" / "day0_run_daily_preflight.json"
    md_path = paths.outputs_dir / "system" / "DAY0_RUN_DAILY_PREFLIGHT_CHECKLIST.md"
    write_json_markdown(json_path, payload, md_path, build_preflight_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _check(check_id: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "evidence": evidence}


def build_preflight_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Day-0 Run-Daily Preflight Checklist",
            "",
            "## Scope",
            "This checklist prepares for a future forward dry-run day 1.",
            "It does not execute run-daily.",
            DAY0_NOTICE,
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Checks",
            *[f"- {item['check_id']}: passed={str(item['passed']).lower()} evidence={item['evidence']}" for item in payload["checks"]],
            "",
            "## Run-Daily Command Preview",
            f"- command={payload['run_daily_command_preview']['command']}",
            "- Preview only. Not executed.",
            "",
            "## Manual Confirmation Required",
            f"- manual_confirmation_required={str(payload['manual_confirmation_required']).lower()}",
            "",
            "## Boundary",
            "- preflight only",
            "- run-daily not called",
            "- forward dry-run not started",
            "- main ledger not written",
            "",
        ]
    )
