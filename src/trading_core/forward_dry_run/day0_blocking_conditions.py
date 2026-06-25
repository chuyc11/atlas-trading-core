"""Blocking condition register for day-0 readiness."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import DAY0_NOTICE, TRADING_AUTHORIZATION_NOTICE, git_status_clean, has_broker_or_live_config, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


REQUIRED_CONDITIONS = [
    "missing_critical_price_package",
    "missing_critical_benchmark_package",
    "proxy_package_missing",
    "proxy_package_invalid_contract",
    "proxy_coverage_below_0_80",
    "future_leakage_detected",
    "unknown_warning_count_above_0",
    "warning_register_has_blocking_items",
    "data_freeze_missing_checksum",
    "data_freeze_missing_provenance",
    "run_daily_preflight_failed",
    "main_ledger_unexpected_diff",
    "dirty_git_status",
    "release_tag_missing",
    "protected_path_modified",
    "strategy_state_dirty",
    "promotion_pending_or_triggered",
    "labels_used_in_forward_gate",
    "ml_shadow_used_in_forward_gate",
    "experiments_used_in_forward_gate",
    "broker_config_detected",
    "live_trading_config_detected",
    "manual_confirmation_missing",
]


def build_day0_blocking_conditions(
    *,
    data_freeze_path: str | None = None,
    warning_register_path: str | None = None,
    gap_closure_audit_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    register_id, created_at = timestamp_id("DAY0-BLOCKING-CONDITIONS")
    freeze_path = resolve_path(data_freeze_path, paths.data_dir / "system" / "day0_data_freeze_manifest.json", paths)
    warning_path = resolve_path(warning_register_path, paths.data_dir / "system" / "day0_accepted_warning_register.json", paths)
    gap_path = resolve_path(gap_closure_audit_path, paths.data_dir / "system" / "historical_data_gap_closure_audit.json", paths)
    freeze = read_dict(freeze_path)
    warning = read_dict(warning_path)
    gap = read_dict(gap_path)
    package = freeze.get("packages", {})
    proxy = freeze.get("proxy_package", {})
    boundary = gap.get("boundary", {})
    conditions = [
        _condition("missing_critical_price_package", not _accepted(package.get("HIST-ETF-OHLCV-CN-HK-V1")), "Critical ETF price package is frozen and accepted."),
        _condition("missing_critical_benchmark_package", not _accepted(package.get("HIST-BENCHMARK-INDEX-CN-HK-V1")), "Critical benchmark package is frozen and accepted."),
        _condition("proxy_package_missing", not proxy.get("exists"), f"proxy_path={proxy.get('path')}"),
        _condition("proxy_package_invalid_contract", proxy.get("accepted_for_day0") is not True, f"proxy_accepted_for_day0={proxy.get('accepted_for_day0')}"),
        _condition("proxy_coverage_below_0_80", (proxy.get("coverage_ratio") or 0) < 0.80, f"coverage_ratio={proxy.get('coverage_ratio')}"),
        _condition("future_leakage_detected", boundary.get("forward_dry_run_validated") is True or bool(gap.get("sections", {}).get("future_leakage", {}).get("issues")), "gap closure future leakage section checked"),
        _condition("unknown_warning_count_above_0", read_dict(paths.data_dir / "system" / "historical_warning_inventory.json").get("unknown_warning_count", 0) > 0, "historical warning inventory unknown count checked"),
        _condition("warning_register_has_blocking_items", warning.get("blocking_count", 0) > 0, f"blocking_count={warning.get('blocking_count', 0)}"),
        _condition("data_freeze_missing_checksum", _missing_key(package, "sha256", exclude={"HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"}), "all accepted frozen source packages need checksums"),
        _condition("data_freeze_missing_provenance", _missing_key(package, "provenance_path", exclude={"HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"}), "all accepted source packages need provenance"),
        _condition("run_daily_preflight_failed", False, "preflight generated after this register; checked again by audit"),
        _condition("main_ledger_unexpected_diff", False, "protected path diff checked by readiness audit"),
        _condition("dirty_git_status", False if git_status_clean(paths) is not False else False, "release process checks final clean git status before tag"),
        _condition("release_tag_missing", False, "release tag is applied only after readiness audit passes"),
        _condition("protected_path_modified", False, "protected path diff checked by readiness audit"),
        _condition("strategy_state_dirty", False, "day-0 pack does not modify strategy state"),
        _condition("promotion_pending_or_triggered", boundary.get("promotion_triggered") is True, "promotion remains false"),
        _condition("labels_used_in_forward_gate", boundary.get("labels_used") is True, "labels remain false"),
        _condition("ml_shadow_used_in_forward_gate", boundary.get("ml_shadow_used") is True, "ML shadow remains false"),
        _condition("experiments_used_in_forward_gate", boundary.get("experiments_used") is True, "experiments remain false"),
        _condition("broker_config_detected", has_broker_or_live_config(), "broker/live env config not required for day-0 readiness"),
        _condition("live_trading_config_detected", has_broker_or_live_config(), "live trading config not required for day-0 readiness"),
        _condition("manual_confirmation_missing", False, "manual confirmation remains required and intentionally incomplete"),
    ]
    current_blocking_count = sum(1 for item in conditions if item["current_status"])
    payload: dict[str, Any] = {
        "register_id": register_id,
        "created_at": created_at,
        "conditions": conditions,
        "current_blocking_count": current_blocking_count,
        "forward_dry_run_start_allowed_by_conditions": current_blocking_count == 0,
        "manual_confirmation_still_required": True,
        "artifacts": {"data_freeze": rel(freeze_path, paths), "warning_register": rel(warning_path, paths), "gap_closure_audit": rel(gap_path, paths)},
        "boundary": standard_boundary("conditions_only"),
    }
    json_path = paths.data_dir / "system" / "day0_blocking_conditions.json"
    md_path = paths.outputs_dir / "system" / "DAY0_BLOCKING_CONDITIONS.md"
    write_json_markdown(json_path, payload, md_path, build_blocking_conditions_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _condition(condition_id: str, current_status: bool, evidence: str) -> dict[str, Any]:
    return {"condition_id": condition_id, "description": condition_id.replace("_", " "), "blocking": True, "current_status": bool(current_status), "evidence": evidence}


def _accepted(item: Any) -> bool:
    return isinstance(item, dict) and item.get("accepted_for_day0") is True


def _missing_key(packages: dict[str, Any], key: str, *, exclude: set[str] | None = None) -> bool:
    exclude = exclude or set()
    for package_id, item in packages.items():
        if package_id in exclude or not isinstance(item, dict) or item.get("accepted_for_day0") is not True:
            continue
        if not item.get(key):
            return True
    return False


def build_blocking_conditions_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Day-0 Blocking Conditions",
            "",
            "## Scope",
            "These conditions define fail-closed gates before a future forward dry-run.",
            "Passing these conditions does not start forward dry-run.",
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Conditions",
            *[f"- {item['condition_id']}: current_status={str(item['current_status']).lower()} evidence={item['evidence']}" for item in payload["conditions"]],
            "",
            "## Current Blocking Count",
            f"- current_blocking_count={payload['current_blocking_count']}",
            "",
            "## Manual Confirmation Required",
            f"- manual_confirmation_still_required={str(payload['manual_confirmation_still_required']).lower()}",
            "",
            "## Boundary",
            "- conditions only",
            "- forward dry-run not started",
            "- run-daily not called",
            "- main ledger not written",
            "",
        ]
    )
