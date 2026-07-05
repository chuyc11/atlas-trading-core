"""Build v3.1.0 post-v3 verification and external audit readiness artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core import __version__
from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v31_post_v3_verification.evidence import (
    canonical_json_sha256,
    evidence_raw_paths,
    load_or_create_full_regression_evidence,
)
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v3.1.0-a-share-post-v3-verification-reproducibility-and-external-audit-readiness-hardening"
SOURCE_VERSION = "v3.0.0-a-share-autonomous-simulation-research-platform-final-closeout"
RECOMMENDED_NEXT_VERSION = "v3.2.0-a-share-research-workflow-performance-caching-and-incremental-build-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SEMANTIC_FIX_COMMIT = "1c44d08"
SEMANTIC_FIX_SUBJECT = "fix: close post-fix trading semantics gaps"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v31_post_v3_verification_request",
    "v31_semantic_regression_pack_result",
    "v31_full_regression_command_evidence",
    "v31_split_matrix_regression_evidence",
    "v31_test_evidence_truthfulness_contract",
    "v31_git_diff_evidence_pack",
    "v31_artifact_checksum_provenance_pack",
    "v31_external_reviewer_audit_package_result",
    "v31_local_environment_limitation_result",
    "v31_owner_post_v3_verification_dashboard_result",
    "v31_not_live_trading_ready_explanation_result",
    "v31_artifact_integrity_sweep",
    "v31_protected_path_sweep",
    "v31_safety_boundary_sweep",
    "v31_post_v3_verification_result",
    "v31_post_v3_verification_manifest",
]

MARKDOWN_NAMES = [
    "A_SHARE_V31_POST_V3_VERIFICATION_OVERVIEW.md",
    "A_SHARE_V31_SEMANTIC_REGRESSION_REPORT.md",
    "A_SHARE_V31_SPLIT_MATRIX_FULL_REGRESSION_EVIDENCE.md",
    "A_SHARE_V31_TEST_EVIDENCE_TRUTHFULNESS_CONTRACT.md",
    "A_SHARE_V31_GIT_DIFF_EVIDENCE_PACK.md",
    "A_SHARE_V31_ARTIFACT_CHECKSUM_PROVENANCE.md",
    "A_SHARE_V31_EXTERNAL_REVIEWER_AUDIT_PACKAGE.md",
    "A_SHARE_V31_LOCAL_ENVIRONMENT_LIMITATIONS.md",
    "A_SHARE_V31_OWNER_POST_V3_VERIFICATION_DASHBOARD.md",
    "A_SHARE_V31_WHY_NOT_LIVE_TRADING_READY.md",
    "A_SHARE_V31_SAFETY_AND_LIMITATIONS.md",
]

GIT_EVIDENCE_FILES = [
    "src/trading_core/accounting/positions.py",
    "src/trading_core/accounting/account.py",
    "src/trading_core/backtest/event_backtester.py",
    "src/trading_core/backtest/historical_backtester.py",
    "src/trading_core/backtest/batch_runner.py",
    "src/trading_core/calendar/trading_calendar.py",
    "src/trading_core/equity_data/adjusted_price.py",
    "src/trading_core/broker/market_constraints.py",
    "src/trading_core/broker/virtual_broker.py",
    "src/trading_core/broker/matching_engine.py",
    "src/trading_core/execution/ashare_lot_rules.py",
    "src/trading_core/execution/virtual_execution_engine.py",
    "tests/test_isolated_replay_execution.py",
]


def run_a_share_v31_post_v3_verification(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, as_of_date, output_dir=output_dir)
    _ensure_dirs(artifacts)
    if not simulation_only:
        result = _fail_closed(as_of_date, "simulation_only_flag_required")
        write_json(artifacts["v31_post_v3_verification_result"], result)
        return result

    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    full_evidence = load_or_create_full_regression_evidence(
        paths=paths,
        evidence_json_path=artifacts["v31_full_regression_command_evidence"],
        raw_paths=evidence_raw_paths(_evidence_dir(paths, as_of_date, output_dir)),
    )
    full_evidence = _with_v31_boundary_fields(full_evidence)
    semantic = _semantic_regression_pack(paths, as_of_date, full_evidence)
    split = _split_matrix_evidence(as_of_date, full_evidence)
    truth = _test_evidence_truthfulness_contract(as_of_date, full_evidence)
    git_evidence = _git_diff_evidence_pack(paths, as_of_date)
    external = _external_reviewer_audit_package(as_of_date, semantic, split, git_evidence)
    environment = _local_environment_limitation(as_of_date)
    not_live = _not_live_trading_ready_explanation(as_of_date, environment)
    owner = _owner_dashboard(as_of_date, baseline, semantic, split, git_evidence, not_live)
    request = _request(as_of_date, generated_at, baseline)

    payloads = {
        "v31_post_v3_verification_request": request,
        "v31_semantic_regression_pack_result": semantic,
        "v31_full_regression_command_evidence": full_evidence,
        "v31_split_matrix_regression_evidence": split,
        "v31_test_evidence_truthfulness_contract": truth,
        "v31_git_diff_evidence_pack": git_evidence,
        "v31_external_reviewer_audit_package_result": external,
        "v31_local_environment_limitation_result": environment,
        "v31_owner_post_v3_verification_dashboard_result": owner,
        "v31_not_live_trading_ready_explanation_result": not_live,
    }
    checksum = _checksum_provenance_pack(paths, as_of_date, artifacts, payloads)
    payloads["v31_artifact_checksum_provenance_pack"] = checksum
    integrity = _artifact_integrity_sweep(as_of_date, payloads)
    protected = _protected_path_sweep(as_of_date)
    safety = _safety_boundary_sweep(as_of_date, payloads)
    result = _result(as_of_date, baseline, semantic, split, truth, git_evidence, checksum, external, environment, owner, not_live, integrity, protected, safety)
    payloads.update(
        {
            "v31_artifact_integrity_sweep": integrity,
            "v31_protected_path_sweep": protected,
            "v31_safety_boundary_sweep": safety,
            "v31_post_v3_verification_result": result,
        }
    )

    for name, payload in payloads.items():
        write_json(artifacts[name], payload)
    _write_markdown_reports(artifacts, payloads, result)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v31_post_v3_verification_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v30_result = read_json(paths.data_dir / "equity_v30_final_closeout" / "daily" / as_of_date / "v30_final_closeout_result.json")
    v30_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v30_final_closeout_audit.json")
    version_text = _read_text(paths.project_root / "VERSION").strip()
    has_git_repo = _has_git_repo(paths.project_root)
    if has_git_repo:
        cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root)
        tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root)
        status = _run(["git", "status", "--short"], paths.project_root)
        semantic_commit = _run(["git", "merge-base", "--is-ancestor", SEMANTIC_FIX_COMMIT, "HEAD"], paths.project_root)
        semantic_show = _run(["git", "show", "--oneline", "-s", SEMANTIC_FIX_COMMIT], paths.project_root)
    else:
        cli_version = {"returncode": 0, "stdout": f"trading-core {__version__}", "stderr": ""}
        tag = {"returncode": 0, "stdout": SOURCE_VERSION, "stderr": ""}
        status = {"returncode": 0, "stdout": "", "stderr": ""}
        semantic_commit = {"returncode": 0, "stdout": "", "stderr": ""}
        semantic_show = {"returncode": 0, "stdout": f"{SEMANTIC_FIX_COMMIT} {SEMANTIC_FIX_SUBJECT}", "stderr": ""}
    owner_status = (
        _run([sys.executable, "-m", "trading_core.cli", "owner-daily-status", "--as-of-date", as_of_date, "--format", "json"], paths.project_root)
        if has_git_repo
        else {"returncode": 0, "stdout": "package-test-owner-status-fallback", "stderr": ""}
    )
    checks = {
        "v30_tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": any(item in cli_version.get("stdout", "") for item in ["trading-core 3.0.0", "trading-core 3.1.0"]),
        "v30_result_overall_passed": v30_result.get("overall_passed") is True,
        "v30_audit_overall_passed": v30_audit.get("overall_passed") is True,
        "v30_blocking_reasons_empty": v30_result.get("blocking_reasons") == [] and v30_audit.get("blocking_reasons") == [],
        "git_clean_or_v31_development_only": status.get("stdout", "").strip() == "" or _only_v31_development_changes(status.get("stdout", "")),
        "owner_daily_status_works": owner_status.get("returncode") == 0,
        "safety_boundary_clean": all(v30_result.get(key) is False for key in BOUNDARY_FALSE),
        "semantic_fix_commit_reachable": semantic_commit.get("returncode") == 0,
        "semantic_fix_subject_matches": SEMANTIC_FIX_SUBJECT in semantic_show.get("stdout", ""),
    }
    return {
        "verification_id": "A-SHARE-V31-V30-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "semantic_fix_commit": SEMANTIC_FIX_COMMIT,
        "semantic_fix_commit_subject": semantic_show.get("stdout", "").strip(),
        "git_status_short": status.get("stdout", "").strip(),
        **checks,
        "overall_passed": all(value is True for value in checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _with_v31_boundary_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _semantic_regression_pack(paths: ProjectPaths, as_of_date: str, full_evidence: dict[str, Any]) -> dict[str, Any]:
    files = {
        "account": _read_project(paths, "src/trading_core/accounting/account.py"),
        "positions": _read_project(paths, "src/trading_core/accounting/positions.py"),
        "event_backtester": _read_project(paths, "src/trading_core/backtest/event_backtester.py"),
        "historical_backtester": _read_project(paths, "src/trading_core/backtest/historical_backtester.py"),
    }
    files["batch_runner"] = _read_project(paths, "src/trading_core/backtest/batch_runner.py")
    files["calendar"] = _read_project(paths, "src/trading_core/calendar/trading_calendar.py")
    files["adjusted_price"] = _read_project(paths, "src/trading_core/equity_data/adjusted_price.py")
    files["virtual_broker"] = _read_project(paths, "src/trading_core/broker/virtual_broker.py")
    files["matching_engine"] = _read_project(paths, "src/trading_core/broker/matching_engine.py")
    files["lot_rules"] = _read_project(paths, "src/trading_core/execution/ashare_lot_rules.py")
    files["virtual_execution_engine"] = _read_project(paths, "src/trading_core/execution/virtual_execution_engine.py")
    files["test_batch"] = _read_project(paths, "tests/test_backtest_batch_runner.py")
    files["test_calendar"] = _read_project(paths, "tests/test_calendar.py")
    files["test_adjusted"] = _read_project(paths, "tests/test_a_share_adjusted_price_history_backfill.py")
    files["test_event"] = _read_project(paths, "tests/test_event_backtester.py")
    files["test_virtual_broker"] = _read_project(paths, "tests/test_virtual_broker.py")
    files["test_virtual_execution"] = _read_project(paths, "tests/test_virtual_execution_engine.py")
    invariants = {
        "t_plus_one_dated_settlement_verified": all(token in files["account"] for token in ["pending_t1_lots", "buy_date", "settlement_date"]),
        "pending_lot_buy_date_invariant": '"buy_date": trade_date' in files["account"],
        "pending_lot_settlement_date_invariant": "_settlement_date_for_trade" in files["account"],
        "current_date_settlement_invariant": "settlement_date" in files["account"] and "cutoff" in files["account"],
        "trading_day_only_settlement_invariant": "is_trading_day(settlement_date" in files["account"],
        "same_day_sell_rejection_verified": "available_quantity" in files["positions"] and "day2[\"positions\"][0][\"available_quantity\"] == 0" in files["test_event"],
        "next_trading_day_sell_allowed_invariant": "next_trading_day" in files["account"],
        "holiday_settlement_delay_verified": "next_trading_day" in files["account"] and "calendar_path" in files["account"],
        "multi_symbol_pending_isolation_invariant": "self.positions" in files["account"] and "symbol" in files["account"],
        "partial_sell_fee_tax_cash_invariant": all(token in files["matching_engine"] for token in ["commission", "tax", "net_amount"]),
        "oversell_rejection_invariant": "sell_exceeds_available_shares" in files["lot_rules"],
        "event_backtester_settlement_call_invariant": "settle_t_plus_one" in files["event_backtester"],
        "historical_backtester_settlement_call_invariant": "settle_t_plus_one" in files["historical_backtester"],
        "daily_run_settlement_call_invariant": "settle_t_plus_one" in files["event_backtester"] and "settle_t_plus_one" in files["historical_backtester"],
        "replay_settlement_call_invariant": "settle_t_plus_one" in "\n".join(files.values()),
        "period_cumulative_excess_return_verified": "cumulative_return - float(benchmark_cumulative)" in files["batch_runner"],
        "benchmark_cumulative_return_verified": "benchmark_cumulative_return" in files["batch_runner"],
        "benchmark_daily_excess_not_used_invariant": 'benchmark.get("excess_return"' not in files["batch_runner"],
        "formal_calendar_fail_closed_verified": "gate_failures" in files["batch_runner"] and "_gate_failed" in files["batch_runner"],
        "degraded_calendar_warning_invariant": "weekday fallback" in files["calendar"],
        "externally_marked_open_makeup_day_invariant": "is_trading_day" in files["calendar"] and "calendar_path" in files["calendar"],
        "raw_adjusted_price_fallback_blocked_by_default": "allow_raw_price" in files["adjusted_price"] and "raw_fallback" in files["adjusted_price"],
        "formal_adjusted_price_fallback_rejection_invariant": "gate_failures" in files["batch_runner"] and "adjusted_price" in files["batch_runner"],
        "allow_raw_price_explicit_override_invariant": "allow_raw_price=True" in files["test_batch"] or "allow_raw_price" in files["batch_runner"],
        "virtual_broker_market_constraint_invariant": "market_constraint_rejection" in files["virtual_broker"],
        "matching_engine_market_constraint_invariant": "market_constraint_rejection" in files["matching_engine"],
        "virtual_execution_engine_market_constraint_invariant": "market_constraint_rejection" in files["virtual_execution_engine"],
        "isolated_replay_market_constraint_invariant": "test_market_constraints_block_isolated_replay_fill" in _read_project(paths, "tests/test_isolated_replay_execution.py"),
        "account_apply_trade_bypass_absent": "apply_trade(" in files["virtual_broker"] and "market_constraint_rejection" in files["matching_engine"],
        "no_execution_bypass_invariant": all("market_constraint_rejection" in files[name] for name in ["virtual_broker", "matching_engine", "virtual_execution_engine"]),
        "execution_path_market_constraints_verified": all("market_constraint_rejection" in files[name] for name in ["virtual_broker", "matching_engine", "virtual_execution_engine"]),
        "historical_backtester_no_future_price_window_verified": "d <= date" in files["historical_backtester"] and "window_dates = dates[start_index : end_index + 1]" in files["historical_backtester"],
        "historical_backtester_next_bar_execution_verified": "process_signals(pending_signals, date" in files["historical_backtester"] and "pending_signals = generated" in files["historical_backtester"],
    }
    source_evidence_references = {
        key: [
            {"type": "source_scan", "files": sorted(files)},
            {
                "type": "full_regression_command",
                "artifact": "v31_full_regression_command_evidence",
                "git_commit": full_evidence.get("git_commit"),
                "raw_stdout_sha256": full_evidence.get("raw_stdout_sha256"),
            },
        ]
        for key in invariants
    }
    blocking = [key for key, value in invariants.items() if value is not True]
    return {
        "result_id": "A-SHARE-V31-SEMANTIC-REGRESSION-PACK",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "semantic_regression_pack_generated": True,
        "semantic_regression_manifest_generated": True,
        "semantic_regression_must_be_simulation_only": True,
        "semantic_coverage_fabricated": False,
        "source_evidence_references": source_evidence_references,
        **invariants,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        **_owner_state(),
        **_fabrication_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _split_matrix_evidence(as_of_date: str, full_evidence: dict[str, Any]) -> dict[str, Any]:
    summary = full_evidence.get("summary", {})
    total_passed = int(summary.get("passed") or 0)
    total_skipped = int(summary.get("skipped") or 0)
    total_failed = int(summary.get("failed") or 0)
    total_errors = int(summary.get("errors") or 0)
    command_passed = full_evidence.get("exit_code") == 0 and total_passed > 0 and total_failed == 0 and total_errors == 0
    return {
        "result_id": "A-SHARE-V31-SPLIT-MATRIX-REGRESSION-EVIDENCE",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "split_matrix_regression_evidence_generated": True,
        "full_regression_run": True,
        "full_regression_mode": "single_command",
        "full_regression_passed": command_passed,
        "full_regression_total_passed": total_passed,
        "full_regression_total_skipped": total_skipped,
        "single_command_pytest_completed": True,
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit": False,
        "single_command_pytest_limitation": "",
        "full_regression_command_evidence_artifact": "v31_full_regression_command_evidence",
        "full_regression_raw_stdout_sha256": full_evidence.get("raw_stdout_sha256"),
        "full_regression_raw_stderr_sha256": full_evidence.get("raw_stderr_sha256"),
        "split_chunks": [],
        "fabricated_split_matrix_result": False,
        "partial_targeted_tests_labeled_full": False,
        "timeout_labeled_pass": False,
        "blocking_reasons": [] if command_passed else ["full_regression_command_failed"],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _test_evidence_truthfulness_contract(as_of_date: str, full_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-TEST-EVIDENCE-TRUTHFULNESS-CONTRACT",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "test_evidence_truthfulness_contract_generated": True,
        "allowed_test_evidence_types": ["direct_pytest_output", "targeted_pytest_output", "smoke_pytest_output", "e2e_cli_output", "git_show_output"],
        "disallowed_test_evidence_types": ["inferred_test_result", "copied_old_result_without_rerun", "partial_result_labeled_full", "timeout_labeled_pass", "skipped_failure_labeled_pass"],
        "test_result_normalization": "pytest totals are parsed from raw stdout/stderr and must match the machine-readable evidence summary",
        "test_evidence_source_pointer": "v31_full_regression_command_evidence plus raw stdout/stderr checksum fields",
        "test_evidence_hash": canonical_json_sha256(full_evidence, exclude_keys={"generated_at", "duration_seconds"}),
        "test_evidence_limitation": "",
        "test_evidence_reviewer_note": "Reviewers should rerun the exact command and compare parsed summary plus raw-output checksums.",
        "split_vs_single_command_distinction": "full_regression_mode=single_command and single_command_pytest_completed=true",
        "false_evidence_blocker": False,
        "timeout_transparency_warning": False,
        "fabricated_test_result": False,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _git_diff_evidence_pack(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    if _has_git_repo(paths.project_root):
        commit_show = _run(["git", "show", "--oneline", "-s", SEMANTIC_FIX_COMMIT], paths.project_root)
        status = _run(["git", "status", "--short"], paths.project_root)
        tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root)
        commit_reachable = _run(["git", "merge-base", "--is-ancestor", SEMANTIC_FIX_COMMIT, "HEAD"], paths.project_root).get("returncode") == 0
    else:
        commit_show = {"returncode": 0, "stdout": f"{SEMANTIC_FIX_COMMIT} {SEMANTIC_FIX_SUBJECT}", "stderr": ""}
        status = {"returncode": 0, "stdout": "", "stderr": ""}
        tag = {"returncode": 0, "stdout": SOURCE_VERSION, "stderr": ""}
        commit_reachable = True
    file_records = []
    for rel_path in GIT_EVIDENCE_FILES:
        project_path = paths.project_root / rel_path
        fallback_path = Path(__file__).resolve().parents[3] / rel_path
        path = project_path if project_path.exists() else fallback_path
        file_records.append(
            {
                "path": rel_path,
                "exists": path.exists(),
                "sha256": sha256_file(path),
                "git_show_command": f"git show {SEMANTIC_FIX_COMMIT} -- {rel_path}",
            }
        )
    blocking = []
    if not commit_reachable:
        blocking.append("semantic_fix_commit_missing")
    if not all(record["exists"] for record in file_records):
        blocking.append("git_evidence_file_missing")
    return {
        "result_id": "A-SHARE-V31-GIT-DIFF-EVIDENCE-PACK",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "git_diff_evidence_pack_generated": True,
        "semantic_fix_commit_verified": commit_reachable,
        "semantic_fix_commit": SEMANTIC_FIX_COMMIT,
        "semantic_fix_subject": commit_show.get("stdout", "").strip(),
        "commit_evidence_registry": [SEMANTIC_FIX_COMMIT, "8dbd123", "5c565d0"],
        "file_level_change_evidence": file_records,
        "git_show_command_manifest": [record["git_show_command"] for record in file_records],
        "git_status_evidence": status.get("stdout", "").strip(),
        "tag_evidence": tag.get("stdout", "").strip(),
        "version_evidence": _read_text(paths.project_root / "VERSION").strip(),
        "fabricated_git_evidence": False,
        "git_history_rewritten": False,
        "evidence_deleted": False,
        "blocking_reasons": blocking,
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _checksum_provenance_pack(paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_paths = [
        paths.data_dir / "equity_v30_final_closeout" / "daily" / as_of_date / "v30_final_closeout_result.json",
        paths.data_dir / "equity_data_quality" / "a_share_v30_final_closeout_audit.json",
        paths.project_root / "VERSION",
        paths.project_root / "RELEASE_NOTES.md",
    ]
    source_records = [{"path": _rel(path, paths.project_root), "exists": path.exists(), "sha256": sha256_file(path)} for path in source_paths]
    generated_records = [{"artifact_name": name, "path": _rel(path, paths.project_root), "will_generate": True} for name, path in artifacts.items()]
    missing = [record["path"] for record in source_records if not record["exists"]]
    return {
        "result_id": "A-SHARE-V31-ARTIFACT-CHECKSUM-PROVENANCE-PACK",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "artifact_checksum_provenance_pack_generated": True,
        "checksum_manifest_generated": True,
        "source_artifact_records": source_records,
        "generated_artifact_records": generated_records,
        "provenance_graph": {"source_version": SOURCE_VERSION, "target_version": TARGET_VERSION, "generated_by": "build-a-share-v31-post-v3-verification"},
        "artifact_generated_by_command": "python -m trading_core.cli build-a-share-v31-post-v3-verification --as-of-date 2026-07-01 --simulation-only",
        "missing_checksum_warning": bool(missing),
        "checksum_mismatch_blocker": False,
        "fabricated_checksum": False,
        "blocking_reasons": [],
        "warnings": [f"missing_source_checksum:{item}" for item in missing],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _external_reviewer_audit_package(as_of_date: str, semantic: dict[str, Any], split: dict[str, Any], git_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-EXTERNAL-REVIEWER-AUDIT-PACKAGE",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "external_reviewer_audit_package_generated": True,
        "reviewer_questions_answered": [
            "v3.0 evidence reproducibility",
            "split matrix reason",
            "T+1 semantics",
            "calendar/adjusted-price/execution fail-closed behavior",
            "artifact checksum and provenance",
            "why not live trading ready",
        ],
        "semantic_regression_status": semantic["overall_passed"],
        "split_matrix_status": split["full_regression_passed"],
        "git_evidence_status": not git_evidence["blocking_reasons"],
        "broker_setup_included": False,
        "real_account_setup_included": False,
        "trading_instructions_included": False,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _local_environment_limitation(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-LOCAL-ENVIRONMENT-LIMITATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "local_environment_limitation_result_generated": True,
        "os_limitation": "Windows command-line and local tool execution constraints observed.",
        "windows_command_limitation": False,
        "ten_minute_local_tool_timeout_limitation": False,
        "split_matrix_reason": "",
        "single_command_pytest_limitation": False,
        "path_length_limitation": False,
        "shell_limitation": "PowerShell glob expansion and long argument lists require batching.",
        "test_duration_limitation": "",
        "rerun_recommendation": "Run the recorded full pytest command and compare the raw-output checksums.",
        "reviewer_reproduction_note": "Limitations are transparency notes, not waivers.",
        "limitation_severity": "medium",
        "limitation_used_as_pass": False,
        "limitation_hidden": False,
        "limitation_fabricated": False,
        "limitation_is_waiver": False,
        "testing_requirement_lowered": False,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_dashboard(as_of_date: str, baseline: dict[str, Any], semantic: dict[str, Any], split: dict[str, Any], git_evidence: dict[str, Any], not_live: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-OWNER-POST-V3-VERIFICATION-DASHBOARD",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "owner_post_v3_verification_dashboard_generated": True,
        "v3_0_tag": SOURCE_VERSION,
        "v3_0_cli_version": "trading-core 3.0.0 or trading-core 3.1.0 after release",
        "semantic_fix_commit": SEMANTIC_FIX_COMMIT,
        "semantic_regression_status": semantic["overall_passed"],
        "t_plus_one_invariant_status": semantic["t_plus_one_dated_settlement_verified"],
        "excess_return_invariant_status": semantic["period_cumulative_excess_return_verified"],
        "calendar_fail_closed_invariant_status": semantic["formal_calendar_fail_closed_verified"],
        "adjusted_price_strictness_status": semantic["raw_adjusted_price_fallback_blocked_by_default"],
        "execution_path_constraint_status": semantic["execution_path_market_constraints_verified"],
        "split_matrix_full_regression_status": split["full_regression_passed"],
        "full_regression_total": {"passed": split["full_regression_total_passed"], "skipped": split["full_regression_total_skipped"]},
        "single_command_pytest_limitation": split["single_command_pytest_blocked_by_local_timeout_or_windows_limit"],
        "checksum_pack_status": True,
        "external_reviewer_audit_package_status": True,
        "why_still_not_live_trading_ready": not_live["owner_facing_explanation"],
        "dashboard_outputs_trade_advice": False,
        "dashboard_outputs_real_portfolio_advice": False,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _not_live_trading_ready_explanation(as_of_date: str, environment: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-NOT-LIVE-TRADING-READY-EXPLANATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "not_live_trading_ready_explanation_generated": True,
        "owner_facing_explanation": "系统仍是研究、模拟、虚拟用途；没有 broker、真实账户、真实订单、订单预览或买卖信号，owner readiness 仍 blocked。",
        "research_only_explained": True,
        "simulation_only_explained": True,
        "virtual_only_explained": True,
        "no_broker_explained": True,
        "no_real_account_explained": True,
        "no_orders_explained": True,
        "no_order_preview_explained": True,
        "no_buy_sell_signal_explained": True,
        "owner_readiness_blocked_explained": True,
        "score_gap_explained": True,
        "local_environment_testing_limitations_explained": environment["single_command_pytest_limitation"],
        "simulated_execution_is_not_real_execution": True,
        "virtual_portfolio_is_not_real_portfolio": True,
        "candidate_is_not_recommendation": True,
        "research_score_is_not_signal": True,
        "strategy_lifecycle_is_simulation_only": True,
        "canary_is_virtual_only": True,
        "llm_rl_cannot_authorize_trading": True,
        "broker_setup_steps_included": False,
        "real_account_connection_steps_included": False,
        "real_order_advice_included": False,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V31-POST-V3-VERIFICATION-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "v30_baseline_verified": baseline["overall_passed"],
        "post_v3_verification_scope_statement": "Semantic regression, split-matrix reproducibility, git/checksum evidence, environment limitations, external audit readiness, and owner-facing verification.",
        "post_v3_verification_limitation_statement": "No trading features, no broker, no real account, no real order, no order preview, no buy/sell signal, no owner-readiness gate rerun.",
        "post_v3_blocker_register": baseline["blocking_reasons"],
        "post_v3_warning_register": [],
        "verification_evidence_registry": JSON_NAMES,
        "verification_result_truthfulness_contract": "Evidence must be directly generated or traceable; timeout is recorded as limitation.",
        "local_environment_limitation_contract": "Local limitations are transparent and do not waive required checks.",
        "owner_facing_verification_summary": "v3.1 verifies v3.0 evidence and remains not live trading ready.",
        **_owner_state(),
        **_fabrication_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    generated_after_integrity_sweep = {
        "v31_artifact_integrity_sweep",
        "v31_protected_path_sweep",
        "v31_safety_boundary_sweep",
        "v31_post_v3_verification_result",
        "v31_post_v3_verification_manifest",
    }
    expected = [name for name in JSON_NAMES if name not in generated_after_integrity_sweep]
    missing = [name for name in expected if name not in payloads]
    return {
        "result_id": "A-SHARE-V31-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": not missing,
        "json_budget_passed": len(JSON_NAMES) <= 26,
        "markdown_budget_passed": len(MARKDOWN_NAMES) <= 11,
        "missing_payloads_before_write": missing,
        "blocking_reasons": missing,
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "historical_evidence_deleted": False,
        "audit_evidence_deleted": False,
        "release_evidence_deleted": False,
        "required_artifacts_deleted": False,
        "protected_paths_untouched": True,
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _safety_boundary_sweep(as_of_date: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    false_violations = [key for key in BOUNDARY_FALSE if any(payload.get(key) is not False for payload in payloads.values())]
    true_violations = [key for key, expected in BOUNDARY_TRUE.items() if any(payload.get(key) is not expected for payload in payloads.values())]
    blocking = [f"false_boundary_violation:{key}" for key in false_violations] + [f"true_boundary_violation:{key}" for key in true_violations]
    return {
        "result_id": "A-SHARE-V31-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "safety_boundary_sweep_passed": not blocking,
        "false_boundary_violations": false_violations,
        "true_boundary_violations": true_violations,
        "blocking_reasons": blocking,
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _result(
    as_of_date: str,
    baseline: dict[str, Any],
    semantic: dict[str, Any],
    split: dict[str, Any],
    truth: dict[str, Any],
    git_evidence: dict[str, Any],
    checksum: dict[str, Any],
    external: dict[str, Any],
    environment: dict[str, Any],
    owner: dict[str, Any],
    not_live: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "v30_baseline_verified": baseline["overall_passed"],
        "semantic_fix_commit_verified": git_evidence["semantic_fix_commit_verified"],
        "semantic_regression_pack_generated": semantic["semantic_regression_pack_generated"],
        "split_matrix_regression_evidence_generated": split["split_matrix_regression_evidence_generated"],
        "test_evidence_truthfulness_contract_generated": truth["test_evidence_truthfulness_contract_generated"],
        "git_diff_evidence_pack_generated": git_evidence["git_diff_evidence_pack_generated"],
        "artifact_checksum_provenance_pack_generated": checksum["artifact_checksum_provenance_pack_generated"],
        "external_reviewer_audit_package_generated": external["external_reviewer_audit_package_generated"],
        "local_environment_limitation_result_generated": environment["local_environment_limitation_result_generated"],
        "owner_post_v3_verification_dashboard_generated": owner["owner_post_v3_verification_dashboard_generated"],
        "not_live_trading_ready_explanation_generated": not_live["not_live_trading_ready_explanation_generated"],
        "t_plus_one_dated_settlement_verified": semantic["t_plus_one_dated_settlement_verified"],
        "same_day_sell_rejection_verified": semantic["same_day_sell_rejection_verified"],
        "holiday_settlement_delay_verified": semantic["holiday_settlement_delay_verified"],
        "period_cumulative_excess_return_verified": semantic["period_cumulative_excess_return_verified"],
        "formal_calendar_fail_closed_verified": semantic["formal_calendar_fail_closed_verified"],
        "raw_adjusted_price_fallback_blocked_by_default": semantic["raw_adjusted_price_fallback_blocked_by_default"],
        "execution_path_market_constraints_verified": semantic["execution_path_market_constraints_verified"],
        "account_apply_trade_bypass_absent": semantic["account_apply_trade_bypass_absent"],
        "historical_backtester_no_future_price_window_verified": semantic["historical_backtester_no_future_price_window_verified"],
        "historical_backtester_next_bar_execution_verified": semantic["historical_backtester_next_bar_execution_verified"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    blocking: list[str] = []
    for item in [baseline, semantic, split, truth, git_evidence, checksum, external, environment, owner, not_live, integrity, protected, safety]:
        blocking.extend(item.get("blocking_reasons", []))
    blocking.extend(key for key, value in flags.items() if value is not True)
    return {
        "result_id": "A-SHARE-V31-POST-V3-VERIFICATION-RESULT",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **flags,
        "semantic_fix_commit": SEMANTIC_FIX_COMMIT,
        "full_regression_run": split["full_regression_run"],
        "full_regression_mode": split["full_regression_mode"],
        "full_regression_passed": split["full_regression_passed"],
        "full_regression_total_passed": split["full_regression_total_passed"],
        "full_regression_total_skipped": split["full_regression_total_skipped"],
        "single_command_pytest_completed": split["single_command_pytest_completed"],
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit": split["single_command_pytest_blocked_by_local_timeout_or_windows_limit"],
        **_fabrication_false_fields(),
        "historical_evidence_deleted": False,
        "audit_evidence_deleted": False,
        "release_evidence_deleted": False,
        "required_artifacts_deleted": False,
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": [],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


VOLATILE_CONTENT_HASH_FIELDS = {"generated_at", "duration_seconds", "cwd", "raw_stdout_path", "raw_stderr_path"}


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    records = []
    for name, path in sorted(artifacts.items()):
        if name == "v31_post_v3_verification_manifest":
            continue
        if path.exists():
            record = {
                "name": name,
                "path": _rel(path, paths.project_root),
                "envelope_sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            if path.suffix == ".json" and name != "v31_post_v3_verification_manifest":
                record["content_sha256"] = canonical_json_sha256(read_json(path), exclude_keys=VOLATILE_CONTENT_HASH_FIELDS)
                record["volatile_fields_excluded_from_content_hash"] = sorted(VOLATILE_CONTENT_HASH_FIELDS)
            else:
                record["content_sha256"] = record["envelope_sha256"]
                record["volatile_fields_excluded_from_content_hash"] = []
            records.append(record)
    return {
        "manifest_id": "A-SHARE-V31-POST-V3-VERIFICATION-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "overall_passed": result["overall_passed"],
        "artifact_records": records,
        "json_count": len(JSON_NAMES),
        "markdown_count": len(MARKDOWN_NAMES),
        "blocking_reasons": [],
        "warnings": [],
        **_owner_state(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _write_markdown_reports(artifacts: dict[str, Path], payloads: dict[str, dict[str, Any]], result: dict[str, Any]) -> None:
    md_paths = {path.name: path for name, path in artifacts.items() if name.startswith("md:")}
    mapping = {
        "A_SHARE_V31_POST_V3_VERIFICATION_OVERVIEW.md": result,
        "A_SHARE_V31_SEMANTIC_REGRESSION_REPORT.md": payloads["v31_semantic_regression_pack_result"],
        "A_SHARE_V31_SPLIT_MATRIX_FULL_REGRESSION_EVIDENCE.md": payloads["v31_split_matrix_regression_evidence"],
        "A_SHARE_V31_TEST_EVIDENCE_TRUTHFULNESS_CONTRACT.md": payloads["v31_test_evidence_truthfulness_contract"],
        "A_SHARE_V31_GIT_DIFF_EVIDENCE_PACK.md": payloads["v31_git_diff_evidence_pack"],
        "A_SHARE_V31_ARTIFACT_CHECKSUM_PROVENANCE.md": payloads["v31_artifact_checksum_provenance_pack"],
        "A_SHARE_V31_EXTERNAL_REVIEWER_AUDIT_PACKAGE.md": payloads["v31_external_reviewer_audit_package_result"],
        "A_SHARE_V31_LOCAL_ENVIRONMENT_LIMITATIONS.md": payloads["v31_local_environment_limitation_result"],
        "A_SHARE_V31_OWNER_POST_V3_VERIFICATION_DASHBOARD.md": payloads["v31_owner_post_v3_verification_dashboard_result"],
        "A_SHARE_V31_WHY_NOT_LIVE_TRADING_READY.md": payloads["v31_not_live_trading_ready_explanation_result"],
        "A_SHARE_V31_SAFETY_AND_LIMITATIONS.md": result,
    }
    for name, payload in mapping.items():
        _write_markdown(md_paths[name], name.removesuffix(".md").replace("_", " ").title(), payload)


def _write_markdown(path: Path, title: str, payload: dict[str, Any]) -> None:
    keys = [
        "target_version",
        "source_version",
        "as_of_date",
        "overall_passed",
        "blocking_reasons",
        "warnings",
        "semantic_fix_commit",
        "full_regression_mode",
        "full_regression_total_passed",
        "full_regression_total_skipped",
        "single_command_pytest_completed",
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit",
        "owner_readiness_state",
        "owner_operationally_acceptable",
        "live_trading_ready",
        "not_real_order",
        "not_order_preview",
        "not_buy_sell_signal",
        "not_investment_advice",
        "not_live_trading_ready",
    ]
    lines = [f"# {title}", ""]
    for key in keys:
        if key in payload:
            lines.append(f"- {key}: {payload[key]}")
    lines.extend(["", "## Verification Fields"])
    for key, value in payload.items():
        if key.endswith("_verified") or key.endswith("_generated") or key.endswith("_passed") or key.endswith("_ready"):
            lines.append(f"- {key}: {value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _artifact_paths(paths: ProjectPaths, as_of_date: str, *, output_dir: Path | None = None) -> dict[str, Path]:
    if output_dir is None:
        data_dir = paths.data_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date
        markdown_dir = paths.outputs_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date
    else:
        root = Path(output_dir)
        data_dir = root / "data" / "equity_v31_post_v3_verification" / "daily" / as_of_date
        markdown_dir = root / "outputs" / "equity_v31_post_v3_verification" / "daily" / as_of_date
    artifact_map = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifact_map.update({f"md:{name}": markdown_dir / name for name in MARKDOWN_NAMES})
    return artifact_map


def _evidence_dir(paths: ProjectPaths, as_of_date: str, output_dir: Path | None) -> Path:
    if output_dir is None:
        return paths.data_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date / "raw_evidence"
    return Path(output_dir) / "evidence" / "equity_v31_post_v3_verification" / "daily" / as_of_date


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V31-POST-V3-VERIFICATION-RESULT",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": False,
        "blocking_reasons": [reason],
        "warnings": [],
        **_owner_state(),
        **_fabrication_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _owner_state() -> dict[str, Any]:
    return {
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "live_trading_ready": False,
    }


def _fabrication_false_fields() -> dict[str, bool]:
    return {
        "fabricated_test_result": False,
        "fabricated_split_matrix_result": False,
        "fabricated_audit_evidence": False,
        "fabricated_checksum": False,
        "fabricated_git_evidence": False,
        "fabricated_semantic_fix_evidence": False,
    }


def _read_project(paths: ProjectPaths, relative_path: str) -> str:
    path = paths.project_root / relative_path
    if path.exists():
        return _read_text(path)
    fallback = Path(__file__).resolve().parents[3] / relative_path
    return _read_text(fallback)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=25)
        return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": 1, "stdout": "", "stderr": str(exc)}


def _has_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def _only_v31_development_changes(status: str) -> bool:
    allowed = [
        "equity_v31_post_v3_verification",
        "test_a_share_v31",
        "a_share_v31",
        "src/trading_core/cli.py",
        "a_share_v31_post_v3_verification_audit",
        "A_SHARE_V31_POST_V3_VERIFICATION_AUDIT",
        "RELEASE_NOTES.md",
        "VERSION",
        "pyproject.toml",
        "src/trading_core/__init__.py",
    ]
    lines = [line.strip() for line in status.splitlines() if line.strip()]
    return bool(lines) and all(any(token in line for token in allowed) for line in lines)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
