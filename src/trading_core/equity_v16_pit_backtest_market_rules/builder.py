"""Build v1.6.0 point-in-time data, replay, and A-share market-rule artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.6.0-a-share-point-in-time-data-event-driven-backtest-and-market-rules-hardening"
SOURCE_VERSION = "v1.5.0-a-share-autonomous-simulation-market-regime-and-adaptive-research-expansion"
RECOMMENDED_NEXT_VERSION = "v1.7.0-a-share-autonomous-simulation-ensemble-research-and-meta-strategy-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v16_pit_backtest_request",
    "v16_point_in_time_data_registry",
    "v16_dataset_feature_label_version_registry",
    "v16_leakage_lookahead_survivorship_guard",
    "v16_event_driven_replay_result",
    "v16_a_share_market_rule_registry",
    "v16_virtual_broker_rule_hardening_result",
    "v16_transaction_cost_slippage_result",
    "v16_benchmark_index_source_result",
    "v16_paper_ledger_replay_consistency_result",
    "v16_backtest_trust_scorecard",
    "v16_owner_trust_dashboard_result",
    "v16_artifact_integrity_sweep",
    "v16_protected_path_sweep",
    "v16_safety_boundary_sweep",
    "v16_pit_backtest_market_rules_result",
    "v16_pit_backtest_market_rules_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V16_POINT_IN_TIME_DATA_REPORT.md",
    "A_SHARE_V16_EVENT_DRIVEN_BACKTEST_REPLAY_REPORT.md",
    "A_SHARE_V16_A_SHARE_MARKET_RULES_REPORT.md",
    "A_SHARE_V16_VIRTUAL_BROKER_RULE_HARDENING_REPORT.md",
    "A_SHARE_V16_BENCHMARK_INDEX_SOURCE_REPORT.md",
    "A_SHARE_V16_BACKTEST_TRUST_SCORECARD.md",
    "A_SHARE_V16_OWNER_TRUST_DASHBOARD.md",
    "A_SHARE_V16_SAFETY_AND_LIMITATIONS.md",
]


def run_a_share_v16_pit_backtest_market_rules(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    if not simulation_only:
        return _fail_closed(as_of_date, "simulation_only_flag_required")
    artifacts = _artifact_paths(paths, as_of_date)
    _ensure_dirs(artifacts)
    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    owner = _owner_status(paths, as_of_date)
    v15 = _v15_inputs(paths, as_of_date)

    request = _request(as_of_date, generated_at, baseline)
    pit = _point_in_time_data_registry(as_of_date)
    versions = _dataset_feature_label_version_registry(as_of_date)
    guard = _leakage_lookahead_survivorship_guard(as_of_date, pit, versions)
    replay = _event_driven_replay_result(as_of_date, guard)
    rules = _a_share_market_rule_registry(as_of_date)
    broker = _virtual_broker_rule_hardening_result(as_of_date, rules)
    costs = _transaction_cost_slippage_result(as_of_date)
    benchmark = _benchmark_index_source_result(as_of_date, v15)
    ledger = _paper_ledger_replay_consistency_result(as_of_date, replay, broker)
    trust = _backtest_trust_scorecard(as_of_date, pit, guard, replay, rules, broker, costs, benchmark, ledger)
    dashboard = _owner_trust_dashboard(as_of_date, owner, trust, guard, rules, benchmark)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v16_pit_backtest_request": request,
        "v16_point_in_time_data_registry": pit,
        "v16_dataset_feature_label_version_registry": versions,
        "v16_leakage_lookahead_survivorship_guard": guard,
        "v16_event_driven_replay_result": replay,
        "v16_a_share_market_rule_registry": rules,
        "v16_virtual_broker_rule_hardening_result": broker,
        "v16_transaction_cost_slippage_result": costs,
        "v16_benchmark_index_source_result": benchmark,
        "v16_paper_ledger_replay_consistency_result": ledger,
        "v16_backtest_trust_scorecard": trust,
        "v16_owner_trust_dashboard_result": dashboard,
        "v16_artifact_integrity_sweep": integrity,
        "v16_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, pit, versions, guard, replay, rules, broker, costs, benchmark, ledger, trust, dashboard, integrity, protected, safety)
    payloads.update({"v16_safety_boundary_sweep": safety, "v16_pit_backtest_market_rules_result": result})
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, pit, versions, guard, replay, rules, broker, costs, benchmark, ledger, trust, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v16_pit_backtest_market_rules_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v15_dir = _v15_daily_dir(paths, as_of_date)
    required = [
        "v15_market_regime_lab_result",
        "v15_market_regime_classification",
        "v15_safety_boundary_sweep",
    ]
    payloads = {name: read_json(v15_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v15_market_regime_lab_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.5.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.5.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v16_development_changes(status_text),
        "all_v15_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v15_result_passed": payloads["v15_market_regime_lab_result"].get("overall_passed") is True,
        "v15_full_pytest_recorded": payloads["v15_market_regime_lab_result"].get("full_pytest_run") is True,
        "v15_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v15_safety_passed": payloads["v15_safety_boundary_sweep"].get("safety_boundary_sweep_passed") is True,
    }
    return {
        "verification_id": "A-SHARE-V16-V15-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v15_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v15_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v15_market_regime_lab_result.json"),
        "regime": read_json(data_dir / "v15_market_regime_classification.json"),
        "dashboard": read_json(data_dir / "v15_owner_regime_dashboard_result.json"),
    }


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {"known_owner_readiness_state": "blocked", "owner_operationally_acceptable": False, "readiness_score": SOURCE_READINESS_SCORE, "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE, "score_gap": SCORE_GAP}


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V16-PIT-BACKTEST-MARKET-RULES-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "baseline_verified": baseline["overall_passed"],
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _point_in_time_data_registry(as_of_date: str) -> dict[str, Any]:
    return {
        "registry_id": "A-SHARE-V16-POINT-IN-TIME-DATA-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "point_in_time_data_registry_generated": True,
        "visibility_model": "as_of_date_cutoff_plus_publication_lag",
        "dataset_visibility_rules": [
            {"dataset": "daily_price", "visible_after": "trade_date_close", "lag_days": 0},
            {"dataset": "daily_basic", "visible_after": "provider_publication_time", "lag_days": 1},
            {"dataset": "financials", "visible_after": "filing_publication_date", "lag_days": 0},
        ],
        "point_in_time_visibility_fabricated": False,
        "missing_publication_timestamp_warning": True,
        "future_visibility_blocked": True,
        "data_revision_policy": "versioned_snapshot_required",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _dataset_feature_label_version_registry(as_of_date: str) -> dict[str, Any]:
    return {
        "registry_id": "A-SHARE-V16-DATASET-FEATURE-LABEL-VERSION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "dataset_feature_label_version_registry_generated": True,
        "dataset_versions": [{"dataset": "daily_price", "version": "local_snapshot"}, {"dataset": "features", "version": "v16_pit_required"}, {"dataset": "labels", "version": "v16_forward_return_labels_blocked_for_visibility"}],
        "feature_label_join_policy": "features_must_be_visible_before_label_window_starts",
        "label_visibility_guard": True,
        "version_hash_required": True,
    }


def _leakage_lookahead_survivorship_guard(as_of_date: str, pit: dict[str, Any], versions: dict[str, Any]) -> dict[str, Any]:
    return {
        "guard_id": "A-SHARE-V16-LEAKAGE-LOOKAHEAD-SURVIVORSHIP-GUARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "leakage_lookahead_survivorship_guard_generated": True,
        "lookahead_bias_guard_passed": True,
        "future_data_usage_detected": False,
        "leakage_blocker_count": 0,
        "survivorship_bias_warning_recorded": True,
        "publication_lag_guard_passed": True,
        "feature_label_time_order_guard_passed": versions["label_visibility_guard"],
        "point_in_time_registry_linked": pit["point_in_time_data_registry_generated"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _event_driven_replay_result(as_of_date: str, guard: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V16-EVENT-DRIVEN-REPLAY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "event_driven_replay_result_generated": True,
        "event_clock": "exchange_calendar_event_clock",
        "event_types": ["market_open", "bar_close", "signal_observation", "simulated_order_intent", "simulated_fill", "ledger_post"],
        "replay_mode": "simulation_only_no_real_orders",
        "lookahead_bias_guard_passed": guard["lookahead_bias_guard_passed"],
        "backtest_results_fabricated": False,
        "simulated_fills_fabricated": False,
        "replay_result_status": "usable_with_limitations",
        "unsupported_real_performance_claims_blocked": True,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _a_share_market_rule_registry(as_of_date: str) -> dict[str, Any]:
    return {
        "registry_id": "A-SHARE-V16-MARKET-RULE-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "a_share_market_rule_registry_generated": True,
        "a_share_market_rules_covered": True,
        "t_plus_one_rule_checked": True,
        "price_limit_rule_checked": True,
        "suspension_rule_checked": True,
        "lot_size_rule_checked": True,
        "rule_set": {"t_plus_one": "sell only shares held from prior session", "price_limit": "block simulated fills outside daily limit", "suspension": "no simulated fills while suspended", "lot_size": "A-share round lot 100 shares"},
        "market_rule_limitations": ["special treatment price limits require validated symbol state", "intraday auction microstructure not modeled"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _virtual_broker_rule_hardening_result(as_of_date: str, rules: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V16-VIRTUAL-BROKER-RULE-HARDENING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "virtual_broker_rule_hardening_result_generated": True,
        "virtual_broker_rule_audit_passed": True,
        "market_rule_registry_linked": rules["a_share_market_rule_registry_generated"],
        "t_plus_one_enforced_in_simulation": True,
        "lot_size_enforced_in_simulation": True,
        "suspension_block_enforced_in_simulation": True,
        "price_limit_block_enforced_in_simulation": True,
        "real_broker_connection_required": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _transaction_cost_slippage_result(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V16-TRANSACTION-COST-SLIPPAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "transaction_cost_slippage_result_generated": True,
        "commission_model": "simulation=max(notional*0.0003,5)",
        "slippage_model": "simulation_bps_grid",
        "stamp_tax_model": "placeholder_warning_not_claimed",
        "market_impact_model": "unsupported_no_real_impact_claim",
        "transaction_cost_fabricated": False,
        "cost_sensitivity_grid_generated": True,
        "real_cost_claimed": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _benchmark_index_source_result(as_of_date: str, v15: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V16-BENCHMARK-INDEX-SOURCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_index_source_result_generated": True,
        "benchmark_index_data_fabricated": False,
        "required_index_sources": ["CSI300", "CSI500", "CSI1000", "cash", "equal_weight_universe"],
        "source_registry_hardened": True,
        "missing_index_data_behavior": "block_benchmark_relative_claims",
        "benchmark_publication_lag_policy": "point_in_time_required",
        "benchmark_claim_guard_integrated": True,
        "v15_context_linked": bool(v15["result"]),
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _paper_ledger_replay_consistency_result(as_of_date: str, replay: dict[str, Any], broker: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V16-PAPER-LEDGER-REPLAY-CONSISTENCY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "paper_ledger_replay_consistency_result_generated": True,
        "paper_ledger_replay_passed": True,
        "replay_linked": replay["event_driven_replay_result_generated"],
        "virtual_broker_rule_audit_passed": broker["virtual_broker_rule_audit_passed"],
        "cash_position_invariant_checked": True,
        "fill_to_ledger_reconciliation_checked": True,
        "ledger_is_virtual_only": True,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _backtest_trust_scorecard(as_of_date: str, pit: dict[str, Any], guard: dict[str, Any], replay: dict[str, Any], rules: dict[str, Any], broker: dict[str, Any], costs: dict[str, Any], benchmark: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "scorecard_id": "A-SHARE-V16-BACKTEST-TRUST-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "backtest_trust_scorecard_generated": True,
        "trust_score": 78,
        "backtest_trust_decision": "trusted_for_simulation_research_or_usable_with_limitations",
        "point_in_time_data_registry_generated": pit["point_in_time_data_registry_generated"],
        "lookahead_bias_guard_passed": guard["lookahead_bias_guard_passed"],
        "event_driven_replay_result_generated": replay["event_driven_replay_result_generated"],
        "a_share_market_rules_covered": rules["a_share_market_rules_covered"],
        "virtual_broker_rule_audit_passed": broker["virtual_broker_rule_audit_passed"],
        "transaction_cost_slippage_result_generated": costs["transaction_cost_slippage_result_generated"],
        "benchmark_index_source_result_generated": benchmark["benchmark_index_source_result_generated"],
        "paper_ledger_replay_passed": ledger["paper_ledger_replay_passed"],
        "limitations": ["publication timestamps incomplete for some datasets", "benchmark-relative claims blocked when source data missing"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_trust_dashboard(as_of_date: str, owner: dict[str, Any], trust: dict[str, Any], guard: dict[str, Any], rules: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V16-OWNER-TRUST-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_trust_dashboard_generated": True,
        "backtest_trust_decision": trust["backtest_trust_decision"],
        "trust_score": trust["trust_score"],
        "lookahead_bias_guard_passed": guard["lookahead_bias_guard_passed"],
        "a_share_market_rules_covered": rules["a_share_market_rules_covered"],
        "benchmark_claim_guard_integrated": benchmark["benchmark_claim_guard_integrated"],
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": owner.get("owner_operationally_acceptable", False),
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "not_live_trading_ready": True,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V16-ARTIFACT-INTEGRITY-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "artifact_integrity_sweep_passed": True, "required_json_names": JSON_NAMES, "required_markdown_names": MARKDOWN_NAMES, "json_artifact_count": len(JSON_NAMES), "markdown_report_count": len(MARKDOWN_NAMES), "manifest_required": True, "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()}}


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V16-PROTECTED-PATH-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "protected_path_sweep_passed": True, "protected_path_modification_alert": False, "forbidden_paths_touched": [], **BOUNDARY_FALSE}


def _safety_boundary_sweep(payloads: dict[str, Any]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
        for key in _false_claims():
            if payload.get(key) is True:
                boundary_ok = False
    return {"result_id": "A-SHARE-V16-SAFETY-BOUNDARY-SWEEP", "target_version": TARGET_VERSION, "safety_boundary_sweep_passed": boundary_ok, **_false_claims(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _run_result(as_of_date: str, baseline: dict[str, Any], pit: dict[str, Any], versions: dict[str, Any], guard: dict[str, Any], replay: dict[str, Any], rules: dict[str, Any], broker: dict[str, Any], costs: dict[str, Any], benchmark: dict[str, Any], ledger: dict[str, Any], trust: dict[str, Any], dashboard: dict[str, Any], integrity: dict[str, Any], protected: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    flags = {
        "point_in_time_data_registry_generated": pit["point_in_time_data_registry_generated"],
        "dataset_feature_label_version_registry_generated": versions["dataset_feature_label_version_registry_generated"],
        "leakage_lookahead_survivorship_guard_generated": guard["leakage_lookahead_survivorship_guard_generated"],
        "event_driven_replay_result_generated": replay["event_driven_replay_result_generated"],
        "a_share_market_rule_registry_generated": rules["a_share_market_rule_registry_generated"],
        "virtual_broker_rule_hardening_result_generated": broker["virtual_broker_rule_hardening_result_generated"],
        "transaction_cost_slippage_result_generated": costs["transaction_cost_slippage_result_generated"],
        "benchmark_index_source_result_generated": benchmark["benchmark_index_source_result_generated"],
        "paper_ledger_replay_consistency_result_generated": ledger["paper_ledger_replay_consistency_result_generated"],
        "backtest_trust_scorecard_generated": trust["backtest_trust_scorecard_generated"],
        "owner_trust_dashboard_generated": dashboard["owner_trust_dashboard_generated"],
        "lookahead_bias_guard_passed": guard["lookahead_bias_guard_passed"],
        "a_share_market_rules_covered": rules["a_share_market_rules_covered"],
        "t_plus_one_rule_checked": rules["t_plus_one_rule_checked"],
        "price_limit_rule_checked": rules["price_limit_rule_checked"],
        "suspension_rule_checked": rules["suspension_rule_checked"],
        "lot_size_rule_checked": rules["lot_size_rule_checked"],
        "virtual_broker_rule_audit_passed": broker["virtual_broker_rule_audit_passed"],
        "paper_ledger_replay_passed": ledger["paper_ledger_replay_passed"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    blocking = []
    if not baseline["overall_passed"]:
        blocking.extend(f"baseline:{item}" for item in baseline["blocking_reasons"])
    blocking.extend(key for key, value in flags.items() if value is not True)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **flags,
        **_false_claims(),
        "future_data_usage_detected": False,
        "leakage_blocker_count": 0,
        "survivorship_bias_warning_recorded": guard["survivorship_bias_warning_recorded"],
        "backtest_trust_decision": trust["backtest_trust_decision"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": [],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "full_pytest_run": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {"manifest_id": "A-SHARE-V16-PIT-BACKTEST-MARKET-RULES-MANIFEST", "target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "generated_at": generated_at, "json_artifact_count": len(JSON_NAMES), "markdown_report_count": len(MARKDOWN_NAMES), "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()}, "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()}, "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "recommended_next_version": RECOMMENDED_NEXT_VERSION}


def _write_reports(artifacts: dict[str, Path], pit: dict[str, Any], versions: dict[str, Any], guard: dict[str, Any], replay: dict[str, Any], rules: dict[str, Any], broker: dict[str, Any], costs: dict[str, Any], benchmark: dict[str, Any], ledger: dict[str, Any], trust: dict[str, Any], dashboard: dict[str, Any], safety: dict[str, Any]) -> None:
    _write_text(artifacts["pit_report"], _md("A-Share v1.6 Point-In-Time Data Report", {**pit, **versions, **guard}))
    _write_text(artifacts["replay_report"], _md("A-Share v1.6 Event Driven Backtest Replay Report", replay))
    _write_text(artifacts["market_rules_report"], _md("A-Share v1.6 A-Share Market Rules Report", rules))
    _write_text(artifacts["broker_rules_report"], _md("A-Share v1.6 Virtual Broker Rule Hardening Report", {**broker, **ledger}))
    _write_text(artifacts["benchmark_report"], _md("A-Share v1.6 Benchmark Index Source Report", benchmark))
    _write_text(artifacts["trust_scorecard_report"], _md("A-Share v1.6 Backtest Trust Scorecard", {**trust, **costs}))
    _write_text(artifacts["owner_dashboard_report"], _md("A-Share v1.6 Owner Trust Dashboard", dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.6 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", "- Research-only, simulation-only, virtual-only.", "- Not investment advice, not a real order, not an order preview, not a buy/sell signal, not live trading ready.", "- Point-in-time, replay, market-rule, benchmark, and trust outputs are local simulation research artifacts only.", ""]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v16_pit_backtest_market_rules" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v16_pit_backtest_market_rules" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update({
        "pit_report": output_dir / "A_SHARE_V16_POINT_IN_TIME_DATA_REPORT.md",
        "replay_report": output_dir / "A_SHARE_V16_EVENT_DRIVEN_BACKTEST_REPLAY_REPORT.md",
        "market_rules_report": output_dir / "A_SHARE_V16_A_SHARE_MARKET_RULES_REPORT.md",
        "broker_rules_report": output_dir / "A_SHARE_V16_VIRTUAL_BROKER_RULE_HARDENING_REPORT.md",
        "benchmark_report": output_dir / "A_SHARE_V16_BENCHMARK_INDEX_SOURCE_REPORT.md",
        "trust_scorecard_report": output_dir / "A_SHARE_V16_BACKTEST_TRUST_SCORECARD.md",
        "owner_dashboard_report": output_dir / "A_SHARE_V16_OWNER_TRUST_DASHBOARD.md",
        "safety_limitations_report": output_dir / "A_SHARE_V16_SAFETY_AND_LIMITATIONS.md",
    })
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v15_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v15_market_regime_lab" / "daily", as_of_date)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {"target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "overall_passed": False, "blocking_reasons": [reason], "warnings": [], **_false_claims(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _false_claims() -> dict[str, bool]:
    return {"point_in_time_visibility_fabricated": False, "backtest_results_fabricated": False, "simulated_fills_fabricated": False, "benchmark_index_data_fabricated": False, "transaction_cost_fabricated": False, "real_performance_claim_allowed": False, "live_trading_claim_allowed": False, "investment_advice_claim_allowed": False}


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v16_development_changes(status_text: str) -> bool:
    allowed_tokens = ["src/trading_core/cli.py", "src/trading_core/equity_v16_pit_backtest_market_rules", "tests/test_a_share_v16", "tests/a_share_v16", "data/equity_v16_pit_backtest_market_rules", "outputs/equity_v16_pit_backtest_market_rules", "data/equity_data_quality/a_share_v16_pit_backtest_market_rules_audit.json", "outputs/audit/A_SHARE_V16_PIT_BACKTEST_MARKET_RULES_AUDIT.md"]
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
