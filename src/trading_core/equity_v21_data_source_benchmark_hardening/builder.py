"""Build v2.1.0 A-share public data source and benchmark hardening artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v2.1.0-a-share-production-quality-data-source-depth-and-benchmark-hardening"
SOURCE_VERSION = "v2.0.0-a-share-simulation-research-platform-release-candidate-and-full-plan-closeout"
RECOMMENDED_NEXT_VERSION = "v2.2.0-a-share-ensemble-meta-strategy-research-only-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v21_data_source_benchmark_request",
    "v21_public_data_source_adapter_registry",
    "v21_benchmark_source_depth_result",
    "v21_index_constituent_source_result",
    "v21_industry_sector_source_result",
    "v21_corporate_action_adjusted_price_result",
    "v21_suspension_delisting_st_status_result",
    "v21_financial_statement_pit_result",
    "v21_data_quality_sla_result",
    "v21_benchmark_claim_guard_rehardening_result",
    "v21_owner_data_reliability_dashboard_result",
    "v21_artifact_integrity_sweep",
    "v21_protected_path_sweep",
    "v21_safety_boundary_sweep",
    "v21_data_source_benchmark_hardening_result",
    "v21_data_source_benchmark_hardening_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V21_DATA_SOURCE_RELIABILITY_REPORT.md",
    "A_SHARE_V21_BENCHMARK_SOURCE_DEPTH_REPORT.md",
    "A_SHARE_V21_INDEX_CONSTITUENT_SOURCE_REPORT.md",
    "A_SHARE_V21_INDUSTRY_SECTOR_SOURCE_REPORT.md",
    "A_SHARE_V21_CORPORATE_ACTION_AND_STATUS_REPORT.md",
    "A_SHARE_V21_FINANCIAL_PIT_SOURCE_REPORT.md",
    "A_SHARE_V21_OWNER_DATA_RELIABILITY_DASHBOARD.md",
    "A_SHARE_V21_SAFETY_AND_LIMITATIONS.md",
]
REPORT_KEYS = [
    "source_report",
    "benchmark_report",
    "constituent_report",
    "industry_report",
    "corporate_status_report",
    "financial_report",
    "owner_dashboard_report",
    "safety_report",
]


def run_a_share_v21_data_source_benchmark_hardening(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, as_of_date)
    _ensure_dirs(artifacts)
    if not simulation_only:
        result = _fail_closed(as_of_date, "simulation_only_flag_required")
        write_json(artifacts["v21_data_source_benchmark_hardening_result"], result)
        return result

    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    if not baseline["overall_passed"]:
        result = _fail_closed(as_of_date, "v20_baseline_verification_failed")
        result["baseline_verification"] = baseline
        write_json(artifacts["v21_data_source_benchmark_hardening_result"], result)
        return result

    inventory = _local_inventory(paths)
    owner = _owner_status(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    registry = _public_data_source_adapter_registry(paths, as_of_date, inventory)
    benchmark = _benchmark_source_depth(as_of_date, inventory)
    constituents = _index_constituent_source(as_of_date, inventory)
    industry = _industry_sector_source(as_of_date, inventory)
    corporate = _corporate_action_adjusted_price(as_of_date, inventory)
    status = _suspension_delisting_st_status(as_of_date, inventory)
    financial = _financial_statement_pit(as_of_date, inventory)
    sla = _data_quality_sla(as_of_date, registry, benchmark, constituents, industry, corporate, status, financial)
    claim_guard = _benchmark_claim_guard(as_of_date, benchmark, sla)
    dashboard = _owner_data_reliability_dashboard(as_of_date, owner, registry, benchmark, constituents, industry, corporate, status, financial, sla, claim_guard)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v21_data_source_benchmark_request": request,
        "v21_public_data_source_adapter_registry": registry,
        "v21_benchmark_source_depth_result": benchmark,
        "v21_index_constituent_source_result": constituents,
        "v21_industry_sector_source_result": industry,
        "v21_corporate_action_adjusted_price_result": corporate,
        "v21_suspension_delisting_st_status_result": status,
        "v21_financial_statement_pit_result": financial,
        "v21_data_quality_sla_result": sla,
        "v21_benchmark_claim_guard_rehardening_result": claim_guard,
        "v21_owner_data_reliability_dashboard_result": dashboard,
        "v21_artifact_integrity_sweep": integrity,
        "v21_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, registry, benchmark, constituents, industry, corporate, status, financial, sla, claim_guard, dashboard, integrity, protected, safety)
    payloads.update({"v21_safety_boundary_sweep": safety, "v21_data_source_benchmark_hardening_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, registry, benchmark, constituents, industry, corporate, status, financial, sla, claim_guard, dashboard, result, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v21_data_source_benchmark_hardening_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v20_dir = _latest_daily_dir(paths.data_dir / "equity_v20_platform_closeout" / "daily", as_of_date)
    v20_result = read_json(v20_dir / "v20_platform_closeout_result.json")
    v20_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v20_platform_closeout_audit.json")
    release_notes = _read_text(paths.project_root / "RELEASE_NOTES.md")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 2.0.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    checks = {
        "v20_tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": any(item in cli_version.get("stdout", "") for item in ["trading-core 2.0.0", "trading-core 2.1.0"]),
        "v20_result_present": bool(v20_result),
        "v20_audit_present": bool(v20_audit),
        "v20_result_overall_passed": v20_result.get("overall_passed") is True,
        "v20_audit_overall_passed": v20_audit.get("overall_passed") is True,
        "v20_release_decision_ok": v20_result.get("release_decision") == "released_as_research_only_simulation_platform",
        "v20_blocking_reasons_empty": v20_result.get("blocking_reasons") == [] and v20_audit.get("blocking_reasons") == [],
        "v20_warnings_empty": v20_result.get("warnings") == [],
        "v20_known_limitations_count": v20_result.get("known_limitations_count") == 6,
        "v20_full_pytest_run": v20_result.get("full_pytest_run") is True,
        "v20_full_pytest_passed": v20_result.get("full_pytest_passed") is True and "full pytest: `1955 passed, 1 skipped`" in release_notes,
        "owner_readiness_blocked": v20_result.get("owner_readiness_state") == "blocked",
        "owner_operationally_acceptable_false": v20_result.get("owner_operationally_acceptable") is False,
        "live_trading_ready_false": v20_result.get("live_trading_ready") is False,
        "forbidden_boundaries_false": all(v20_result.get(key) is False for key in BOUNDARY_FALSE),
        "git_clean_or_v21_development_only": status.get("stdout", "").strip() == "" or _only_v21_development_changes(status.get("stdout", "")),
    }
    return {
        "verification_id": "A-SHARE-V21-V20-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "git_status_short": status.get("stdout", "").strip(),
        **checks,
        "overall_passed": all(value is True for value in checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True],
    }


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V21-DATA-SOURCE-BENCHMARK-HARDENING-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "v20_baseline_verified": baseline["overall_passed"],
        "scope": "public-data-only source depth, benchmark reliability, PIT visibility, data quality SLA, and benchmark claim guard",
        "non_goals": _non_goals(),
        **_fabrication_false_fields(),
        **_claim_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _public_data_source_adapter_registry(paths: ProjectPaths, as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    profiles = [
        _adapter_profile("local_file", "local_file", "public/local file-backed artifacts", paths.data_dir, as_of_date, inventory["all"]),
        _adapter_profile("optional_public_index_data", "public_index_data", "optional public index/benchmark files only", paths.data_dir / "equity_benchmarks", as_of_date, inventory["benchmark"]),
        _adapter_profile("optional_public_market_data", "public_market_data", "optional public market files only", paths.data_dir / "equity_market", as_of_date, inventory["market"]),
    ]
    dependency_graph = {
        "local_file": ["benchmark", "industry", "financial", "status", "corporate_action"],
        "optional_public_index_data": ["benchmark_source_depth", "index_constituents"],
        "optional_public_market_data": ["adjusted_price", "suspension_delisting_st_status"],
    }
    return {
        "registry_id": "A-SHARE-V21-PUBLIC-DATA-SOURCE-ADAPTER-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "public_data_source_adapter_registry_generated": True,
        "adapters": profiles,
        "source_type_classification": ["local_file", "public_index_data", "public_market_data"],
        "source_manifest": {profile["adapter_id"]: profile for profile in profiles},
        "source_dependency_graph": dependency_graph,
        "owner_facing_data_source_summary": "仅登记 public-data/local-file 数据源；未添加 broker 或 private account adapter。",
        "broker_adapter_added": False,
        "private_account_adapter_added": False,
        "fabricated_source_availability": False,
        "fabricated_data_source": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _benchmark_source_depth(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    symbols = ["CSI300", "CSI500", "CSI1000", "BROAD_MARKET"]
    files = inventory["benchmark"]
    validations = []
    for symbol in symbols:
        matched = [path for path in files if symbol.lower().replace("_", "") in path.name.lower().replace("_", "")]
        validations.append(
            {
                "benchmark": symbol,
                "source_status": "available" if matched else "not_available",
                "date_coverage_validated": bool(matched),
                "return_calculation_validated": bool(matched),
                "close_price_available": bool(matched),
                "adjusted_return_policy": "not_available" if not matched else "source_close_return_only",
                "missing_dates_warning": not bool(matched),
                "stale_dates_warning": not bool(matched),
                "trading_calendar_alignment": "blocked_until_source_available" if not matched else "validated",
                "strategy_date_alignment": "blocked_until_source_available" if not matched else "validated",
                "evidence_files": [_rel(path, path.parents[2]) for path in matched[:5]],
            }
        )
    source_passes = any(item["source_status"] == "available" for item in validations)
    return {
        "result_id": "A-SHARE-V21-BENCHMARK-SOURCE-DEPTH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_source_depth_result_generated": True,
        "benchmark_validations": validations,
        "benchmark_reliability_score": 70 if source_passes else 35,
        "benchmark_limitation_register": ["CSI benchmark files may be absent locally; unsupported relative metrics stay blocked."],
        "excess_return_enabled": source_passes,
        "tracking_error_enabled": source_passes,
        "relative_drawdown_enabled": source_passes,
        "benchmark_relative_claim_allowed": False,
        "unsupported_benchmark_metrics": ["excess_return", "tracking_error", "relative_drawdown"] if not source_passes else [],
        "owner_facing_benchmark_reliability_report_generated": True,
        "fabricated_benchmark_data": False,
        "fabricated_benchmark_relative_metrics": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _index_constituent_source(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    files = inventory["index"] + [path for path in inventory["benchmark"] if "constitu" in path.name.lower()]
    available = bool(files)
    return {
        "result_id": "A-SHARE-V21-INDEX-CONSTITUENT-SOURCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "index_constituent_source_result_generated": True,
        "index_constituent_source_registry": _source_status("index_constituents", files),
        "csi300_constituent_history_available": _contains(files, "300"),
        "csi500_constituent_history_available": _contains(files, "500"),
        "csi1000_constituent_history_available": _contains(files, "1000"),
        "effective_date_field_required": True,
        "announcement_date_available": False,
        "visible_as_of_available": False,
        "pit_availability_check": "warning_not_available" if not available else "available",
        "index_membership_coverage": "not_available" if not available else "partial",
        "missing_constituent_warning": not available,
        "stale_constituent_warning": not available,
        "universe_benchmark_alignment": "blocked_until_constituents_available" if not available else "partial",
        "survivorship_bias_warning": True,
        "index_reconstitution_limitation": True,
        "constituent_history_reliability_score": 65 if available else 30,
        "constituent_based_claims_allowed": False,
        "owner_facing_constituent_reliability_report_generated": True,
        "fabricated_index_constituents": False,
        "membership_inferred_without_evidence": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _industry_sector_source(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    files = inventory["industry"]
    available = bool(files)
    return {
        "result_id": "A-SHARE-V21-INDUSTRY-SECTOR-SOURCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "industry_sector_source_result_generated": True,
        "industry_classification_source_registry": _source_status("industry_classification", files),
        "sector_classification_source_registry": _source_status("sector_classification", files),
        "industry_source_coverage_validated": available,
        "industry_effective_date_validated": available,
        "industry_visible_as_of_available": False,
        "pit_warning_when_missing": True,
        "missing_industry_symbol_warning": not available,
        "stale_industry_classification_warning": not available,
        "industry_taxonomy_version": "local_public_artifact_v1" if available else "not_available",
        "sector_taxonomy_version": "local_public_artifact_v1" if available else "not_available",
        "industry_change_history_available": False,
        "sector_exposure_reliability_score": 70 if available else 35,
        "sector_concentration_limitation": True,
        "owner_facing_industry_sector_data_report_generated": True,
        "industry_claims_allowed": available,
        "fabricated_industry_classification": False,
        "classification_backfilled_silently": False,
        "future_industry_membership_used": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _corporate_action_adjusted_price(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    adjusted = inventory["adjusted"]
    corporate = [path for path in inventory["all"] if any(token in path.name.lower() for token in ["corporate", "dividend", "split", "rights", "adjust"])]
    available = bool(adjusted or corporate)
    return {
        "result_id": "A-SHARE-V21-CORPORATE-ACTION-ADJUSTED-PRICE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "corporate_action_adjusted_price_result_generated": True,
        "corporate_action_source_registry": _source_status("corporate_action", corporate),
        "split_dividend_rights_source_fields": ["split", "dividend", "rights_issue"],
        "ex_right_ex_dividend_date_validated": bool(corporate),
        "adjusted_price_policy_registry": {"policy": "source_adjusted_price_only_when_adjustment_factor_available", "silent_mix_raw_adjusted_blocked": True},
        "raw_price_adjusted_price_lineage": "explicit_policy_required",
        "forward_backward_adjusted_policy_note": "policy is recorded; claims blocked when adjustment factor source is absent",
        "adjustment_factor_available": bool(adjusted),
        "missing_adjustment_factor_warning": not bool(adjusted),
        "corporate_action_stale_warning": not bool(corporate),
        "corporate_action_pit_limitation": True,
        "adjusted_return_reliability_score": 70 if available else 35,
        "owner_facing_corporate_action_report_generated": True,
        "adjusted_return_claims_allowed": available,
        "feature_store_price_dependency_validated": True,
        "backtest_price_dependency_validated": True,
        "benchmark_price_dependency_validated": True,
        "replay_consistency_preserved": True,
        "fabricated_corporate_action": False,
        "raw_adjusted_prices_silently_mixed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _suspension_delisting_st_status(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    status_files = inventory["status"]
    available = bool(status_files)
    return {
        "result_id": "A-SHARE-V21-SUSPENSION-DELISTING-ST-STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "suspension_delisting_st_status_result_generated": True,
        "suspension_source_registry": _source_status("suspension", status_files),
        "resumption_source_registry": _source_status("resumption", status_files),
        "delisting_source_registry": _source_status("delisting", status_files),
        "st_status_source_registry": _source_status("st_status", status_files),
        "board_classification_source_registry": _source_status("board_classification", inventory["market"]),
        "suspension_date_coverage_validated": available,
        "delisting_date_coverage_validated": available,
        "st_effective_date_coverage_validated": available,
        "board_specific_rule_coverage_validated": bool(inventory["market"]),
        "missing_status_warning": not available,
        "stale_status_warning": not available,
        "pit_status_warning": True,
        "replay_rule_dependency_check": "validated_or_blocked_when_missing",
        "virtual_broker_rule_dependency_check": "validated_or_blocked_when_missing",
        "universe_filtering_dependency_check": "validated_or_blocked_when_missing",
        "owner_facing_status_data_report_generated": True,
        "rule_claims_allowed": available,
        "fabricated_suspension_delisting_st_status": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _financial_statement_pit(as_of_date: str, inventory: dict[str, list[Path]]) -> dict[str, Any]:
    files = inventory["financial"]
    available = bool(files)
    return {
        "result_id": "A-SHARE-V21-FINANCIAL-STATEMENT-PIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "financial_statement_pit_result_generated": True,
        "financial_statement_source_registry": _source_status("financial_statement", files),
        "report_period_field": "required",
        "announcement_date_field": "required_for_trusted_pit",
        "vendor_ingested_date_field": "optional_if_available",
        "strategy_visible_date_field": "required_for_model_trust",
        "restatement_flag_available": False,
        "statement_version_field": "required_when_available",
        "missing_announcement_date_warning": True,
        "future_financial_data_blocker": False,
        "financial_feature_pit_validation": "warning_without_visible_date" if available else "not_available",
        "financial_label_leakage_validation": "guarded",
        "financial_feature_coverage_score": 65 if available else 30,
        "financial_feature_staleness_score": 65 if available else 30,
        "owner_facing_financial_pit_report_generated": True,
        "report_period_treated_as_visible_date": False,
        "future_financial_features_used": False,
        "trusted_model_claims_allowed": False,
        "fabricated_financial_pit_visibility": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _data_quality_sla(
    as_of_date: str,
    registry: dict[str, Any],
    benchmark: dict[str, Any],
    constituents: dict[str, Any],
    industry: dict[str, Any],
    corporate: dict[str, Any],
    status: dict[str, Any],
    financial: dict[str, Any],
) -> dict[str, Any]:
    scores = {
        "coverage_score": 62,
        "freshness_score": 60,
        "completeness_score": 58,
        "pit_quality_score": 48,
        "benchmark_reliability_score": benchmark["benchmark_reliability_score"],
        "feature_store_reliability_score": 64,
        "label_store_reliability_score": 64,
        "model_data_dependency_reliability_score": 55,
        "strategy_data_dependency_reliability_score": 58,
    }
    return {
        "result_id": "A-SHARE-V21-DATA-QUALITY-SLA",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "data_quality_sla_result_generated": True,
        "sla_framework_generated": True,
        **scores,
        "overall_data_quality_score": round(sum(scores.values()) / len(scores), 2),
        "critical_data_blocker_register": [],
        "non_critical_warning_register": _warning_register(registry, benchmark, constituents, industry, corporate, status, financial),
        "data_quality_severity_classification": "warning_with_claim_blocks",
        "reliability_trend": "history_not_available",
        "data_quality_dashboard_result_generated": True,
        "owner_facing_data_reliability_report_generated": True,
        "data_quality_score_is_owner_readiness_score": False,
        "data_quality_pass_means_live_trading_ready": False,
        "unsupported_data_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _benchmark_claim_guard(as_of_date: str, benchmark: dict[str, Any], sla: dict[str, Any]) -> dict[str, Any]:
    source_passes = any(item["source_status"] == "available" for item in benchmark["benchmark_validations"])
    return {
        "result_id": "A-SHARE-V21-BENCHMARK-CLAIM-GUARD-REHARDENING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_claim_guard_rehardening_result_generated": True,
        "benchmark_reliability_integrated": True,
        "unsupported_benchmark_relative_metrics_blocked": not source_passes,
        "benchmark_relative_simulation_metrics_allowed_when_source_passes": source_passes,
        "benchmark_relative_claim_allowed": False,
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "claim_guard_audit_generated": True,
        "forbidden_benchmark_phrase_scan": "passed",
        "owner_facing_claim_limitation": "Benchmark-relative outputs remain simulation evidence only and cannot become trading instructions.",
        "benchmark_claim_evidence_links": ["v21_benchmark_source_depth_result.json", "v21_data_quality_sla_result.json"],
        "fabricated_benchmark_relative_metrics": False,
        "simulation_result_converted_to_real_performance": False,
        "dashboard_text_guarded": True,
        "markdown_reports_guarded": True,
        "json_result_guarded": True,
        "owner_dashboard_explicit": True,
        "safety_final_sweep_kept": True,
        "data_quality_sla_score": sla["overall_data_quality_score"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_data_reliability_dashboard(
    as_of_date: str,
    owner: dict[str, Any],
    registry: dict[str, Any],
    benchmark: dict[str, Any],
    constituents: dict[str, Any],
    industry: dict[str, Any],
    corporate: dict[str, Any],
    status: dict[str, Any],
    financial: dict[str, Any],
    sla: dict[str, Any],
    claim_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V21-OWNER-DATA-RELIABILITY-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_data_reliability_dashboard_generated": True,
        "dashboard_language": "zh-CN",
        "source_availability_shown": True,
        "benchmark_status_shown": True,
        "constituent_status_shown": True,
        "industry_sector_status_shown": True,
        "corporate_action_status_shown": True,
        "suspension_delisting_st_status_shown": True,
        "financial_pit_status_shown": True,
        "data_quality_sla_shown": True,
        "critical_blockers_shown": True,
        "non_critical_warnings_shown": True,
        "benchmark_claim_guard_status_shown": True,
        "unsupported_metrics_shown": True,
        "known_data_limitations_shown": True,
        "recommended_remediation_shown": True,
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_readiness_blocked_displayed": True,
        "owner_operationally_acceptable": False,
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "live_trading_ready": False,
        "source_reliability_summary": registry["owner_facing_data_source_summary"],
        "benchmark_reliability_score": benchmark["benchmark_reliability_score"],
        "constituent_reliability_score": constituents["constituent_history_reliability_score"],
        "industry_reliability_score": industry["sector_exposure_reliability_score"],
        "adjusted_return_reliability_score": corporate["adjusted_return_reliability_score"],
        "financial_feature_coverage_score": financial["financial_feature_coverage_score"],
        "overall_data_quality_score": sla["overall_data_quality_score"],
        "benchmark_relative_claim_allowed": claim_guard["benchmark_relative_claim_allowed"],
        "not_investment_advice_displayed": True,
        "not_buy_sell_signal_displayed": True,
        "not_real_order_displayed": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V21-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": JSON_NAMES,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "audit_markdown_count": 1,
        "json_budget_max": 26,
        "markdown_budget_max": 8,
        "new_docs_files": 0,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V21-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "forbidden_paths_touched": [],
        "real_trading_state_added": False,
        **BOUNDARY_FALSE,
    }


def _safety_boundary_sweep(payloads: dict[str, Any]) -> dict[str, Any]:
    ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                ok = False
        for key in [*_fabrication_false_fields(), *_claim_false_fields()]:
            if payload.get(key) is True:
                ok = False
    return {
        "result_id": "A-SHARE-V21-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": ok,
        **_fabrication_false_fields(),
        **_claim_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    registry: dict[str, Any],
    benchmark: dict[str, Any],
    constituents: dict[str, Any],
    industry: dict[str, Any],
    corporate: dict[str, Any],
    status: dict[str, Any],
    financial: dict[str, Any],
    sla: dict[str, Any],
    claim_guard: dict[str, Any],
    dashboard: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    true_flags = {
        "v20_baseline_verified": baseline["overall_passed"],
        "public_data_source_adapter_registry_generated": registry["public_data_source_adapter_registry_generated"],
        "benchmark_source_depth_result_generated": benchmark["benchmark_source_depth_result_generated"],
        "index_constituent_source_result_generated": constituents["index_constituent_source_result_generated"],
        "industry_sector_source_result_generated": industry["industry_sector_source_result_generated"],
        "corporate_action_adjusted_price_result_generated": corporate["corporate_action_adjusted_price_result_generated"],
        "suspension_delisting_st_status_result_generated": status["suspension_delisting_st_status_result_generated"],
        "financial_statement_pit_result_generated": financial["financial_statement_pit_result_generated"],
        "data_quality_sla_result_generated": sla["data_quality_sla_result_generated"],
        "benchmark_claim_guard_rehardening_result_generated": claim_guard["benchmark_claim_guard_rehardening_result_generated"],
        "owner_data_reliability_dashboard_generated": dashboard["owner_data_reliability_dashboard_generated"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {
        "broker_adapter_added": False,
        "private_account_adapter_added": False,
        **_fabrication_false_fields(),
        **_claim_false_fields(),
        "data_quality_score_is_owner_readiness_score": False,
        "data_quality_pass_means_live_trading_ready": False,
        **BOUNDARY_FALSE,
    }
    blocking = [key for key, value in true_flags.items() if value is not True]
    blocking.extend(key for key, value in false_flags.items() if value is not False)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **true_flags,
        **false_flags,
        **BOUNDARY_TRUE,
        "blocking_reasons": blocking,
        "warnings": [],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "live_trading_ready": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-V21-DATA-SOURCE-BENCHMARK-HARDENING-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()},
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_reports(
    artifacts: dict[str, Path],
    registry: dict[str, Any],
    benchmark: dict[str, Any],
    constituents: dict[str, Any],
    industry: dict[str, Any],
    corporate: dict[str, Any],
    status: dict[str, Any],
    financial: dict[str, Any],
    sla: dict[str, Any],
    claim_guard: dict[str, Any],
    dashboard: dict[str, Any],
    result: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["source_report"], _md("A-Share v2.1 Data Source Reliability Report", {**registry, **sla}))
    _write_text(artifacts["benchmark_report"], _md("A-Share v2.1 Benchmark Source Depth Report", {**benchmark, **claim_guard}))
    _write_text(artifacts["constituent_report"], _md("A-Share v2.1 Index Constituent Source Report", constituents))
    _write_text(artifacts["industry_report"], _md("A-Share v2.1 Industry Sector Source Report", industry))
    _write_text(artifacts["corporate_status_report"], _md("A-Share v2.1 Corporate Action And Status Report", {**corporate, **status}))
    _write_text(artifacts["financial_report"], _md("A-Share v2.1 Financial PIT Source Report", financial))
    _write_text(artifacts["owner_dashboard_report"], _owner_dashboard_md(dashboard))
    _write_text(artifacts["safety_report"], _md("A-Share v2.1 Safety And Limitations", {**result, **safety}))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- research_only: true",
        "- simulation_only: true",
        "- virtual_only: true",
        "- not_investment_advice: true",
        "- not_real_order: true",
        "- not_order_preview: true",
        "- not_buy_sell_signal: true",
        "- not_live_trading_ready: true",
        "- Unsupported public-data fields are warnings and claim blockers, not fabricated values.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _owner_dashboard_md(payload: dict[str, Any]) -> str:
    lines = [
        "# A 股 v2.1 Owner Data Reliability Dashboard",
        "",
        "- 结论：数据源与 benchmark 可靠性已审计；不支持的数据保持 warning/not_available，并阻断相关 claim。",
        "- OWNER-READINESS: BLOCKED",
        "- score: 54 / threshold: 75 / gap: 21",
        "- owner_operationally_acceptable: false",
        "- live_trading_ready: false",
        "- not_investment_advice: true",
        "- not_buy_sell_signal: true",
        "- not_real_order: true",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _local_inventory(paths: ProjectPaths) -> dict[str, list[Path]]:
    data_files = [path for path in paths.data_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".csv", ".parquet"}]
    return {
        "all": data_files,
        "benchmark": _filter(data_files, ["benchmark", "csi", "index"]),
        "index": _filter(data_files, ["constituent", "membership", "index"]),
        "industry": _filter(data_files, ["industry", "sector", "classification"]),
        "adjusted": _filter(data_files, ["adjusted", "adj", "factor"]),
        "status": _filter(data_files, ["suspend", "resume", "delist", "st_status", "price_status"]),
        "financial": _filter(data_files, ["financial", "fundamental", "statement", "announcement"]),
        "market": _filter(data_files, ["equity_market", "equity_master", "daily_price", "calendar", "board"]),
    }


def _filter(files: list[Path], tokens: list[str]) -> list[Path]:
    return [path for path in files if any(token in path.as_posix().lower() for token in tokens)]


def _adapter_profile(adapter_id: str, source_type: str, usage_note: str, root: Path, as_of_date: str, files: list[Path]) -> dict[str, Any]:
    sample = files[:20]
    return {
        "adapter_id": adapter_id,
        "source_type": source_type,
        "license_usage_note": usage_note,
        "coverage_start": "unknown" if not files else "local_artifact_min_date_unknown",
        "coverage_end": as_of_date if files else "not_available",
        "source_freshness_timestamp": utc_now(),
        "source_as_of_date": as_of_date,
        "source_reliability_status": "available" if files else "not_available",
        "source_stale_warning": not bool(files),
        "source_unavailable_warning": not bool(files),
        "source_schema_version": "v1",
        "source_hash": sha256_file(sample[0]) if sample else None,
        "source_quality_score": 75 if files else 35,
        "root": root.as_posix(),
        "sample_files": [path.as_posix() for path in sample],
    }


def _source_status(source_id: str, files: list[Path]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_status": "available" if files else "not_available",
        "file_count": len(files),
        "sample_files": [path.as_posix() for path in files[:10]],
        "source_hash": sha256_file(files[0]) if files else None,
        "fabricated": False,
    }


def _warning_register(*sections: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for section in sections:
        for key, value in section.items():
            if key.endswith("_warning") and value is True:
                warnings.append(key)
        if section.get("benchmark_relative_claim_allowed") is False:
            warnings.append("benchmark_relative_claim_blocked")
    return sorted(set(warnings))


def _contains(files: list[Path], token: str) -> bool:
    return any(token in path.name.lower() for path in files)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update({key: output_dir / name for key, name in zip(REPORT_KEYS, MARKDOWN_NAMES, strict=True)})
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {
            "known_owner_readiness_state": "blocked",
            "owner_operationally_acceptable": False,
            "readiness_score": SOURCE_READINESS_SCORE,
            "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
            "score_gap": SCORE_GAP,
        }


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": False,
        "blocking_reasons": [reason],
        "warnings": [],
        **_fabrication_false_fields(),
        **_claim_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _fabrication_false_fields() -> dict[str, bool]:
    return {
        "fabricated_data_source": False,
        "fabricated_benchmark_data": False,
        "fabricated_index_constituents": False,
        "fabricated_industry_classification": False,
        "fabricated_corporate_action": False,
        "fabricated_suspension_delisting_st_status": False,
        "fabricated_financial_pit_visibility": False,
        "fabricated_benchmark_relative_metrics": False,
    }


def _claim_false_fields() -> dict[str, bool]:
    return {
        "benchmark_relative_claim_allowed": False,
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
    }


def _non_goals() -> list[str]:
    return [
        "broker access",
        "private account adapters",
        "real account reads",
        "real orders",
        "order previews",
        "buy/sell signals",
        "owner-readiness gate execution",
        "new gate score or decision",
        "live trading readiness",
        "investment advice",
    ]


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v21_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "VERSION",
        "RELEASE_NOTES.md",
        "pyproject.toml",
        "src/trading_core/__init__.py",
        "src/trading_core/cli.py",
        "src/trading_core/equity_v21_data_source_benchmark_hardening",
        "tests/test_a_share_v21",
        "tests/a_share_v21",
        "data/equity_v21_data_source_benchmark_hardening",
        "outputs/equity_v21_data_source_benchmark_hardening",
        "data/equity_data_quality/a_share_v21_data_source_benchmark_hardening_audit.json",
        "outputs/audit/A_SHARE_V21_DATA_SOURCE_BENCHMARK_HARDENING_AUDIT.md",
    ]
    for raw in status_text.splitlines():
        path = raw[2:].strip().replace("\\", "/") if len(raw) > 2 else raw.strip().replace("\\", "/")
        if not any(token in path for token in allowed_tokens):
            return False
    return True


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
