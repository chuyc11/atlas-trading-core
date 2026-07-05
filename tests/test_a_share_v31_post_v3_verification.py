from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v31_test_utils import make_v31_paths, v31_json, write_v31_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v31_post_v3_verification.audit import audit_a_share_v31_post_v3_verification
from trading_core.equity_v31_post_v3_verification.builder import (
    DEFAULT_AS_OF_DATE,
    JSON_NAMES,
    MARKDOWN_NAMES,
    RECOMMENDED_NEXT_VERSION,
    SOURCE_VERSION,
    TARGET_VERSION,
    run_a_share_v31_post_v3_verification,
)


def test_v31_build_generates_post_v3_verification_contract(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    result = run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)

    assert result["target_version"] == TARGET_VERSION
    assert result["source_version"] == SOURCE_VERSION
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["warnings"] == []
    assert result["semantic_fix_commit"] == "1c44d08"
    assert result["recommended_next_version"] == RECOMMENDED_NEXT_VERSION
    assert result["owner_readiness_state"] == "blocked"
    assert result["owner_operationally_acceptable"] is False
    assert result["live_trading_ready"] is False


def test_v31_semantic_regression_pack_verifies_core_trading_semantics(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    semantic = v31_json(paths, "v31_semantic_regression_pack_result")

    assert semantic["overall_passed"] is True
    assert semantic["t_plus_one_dated_settlement_verified"] is True
    assert semantic["same_day_sell_rejection_verified"] is True
    assert semantic["holiday_settlement_delay_verified"] is True
    assert semantic["period_cumulative_excess_return_verified"] is True
    assert semantic["formal_calendar_fail_closed_verified"] is True
    assert semantic["raw_adjusted_price_fallback_blocked_by_default"] is True
    assert semantic["execution_path_market_constraints_verified"] is True
    assert semantic["account_apply_trade_bypass_absent"] is True
    assert semantic["historical_backtester_no_future_price_window_verified"] is True
    assert semantic["historical_backtester_next_bar_execution_verified"] is True


def test_v31_split_matrix_evidence_matches_full_regression_totals(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    result = run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    evidence = v31_json(paths, "v31_full_regression_command_evidence")
    split = v31_json(paths, "v31_split_matrix_regression_evidence")

    assert split["full_regression_run"] is True
    assert split["full_regression_mode"] == "single_command"
    assert split["full_regression_passed"] is True
    assert split["full_regression_total_passed"] == evidence["summary"]["passed"]
    assert split["full_regression_total_skipped"] == evidence["summary"]["skipped"]
    assert evidence["raw_stdout_sha256"] == split["full_regression_raw_stdout_sha256"]
    assert result["single_command_pytest_completed"] is True
    assert result["single_command_pytest_blocked_by_local_timeout_or_windows_limit"] is False


def test_v31_truthfulness_git_checksum_and_external_audit_artifacts(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)

    truth = v31_json(paths, "v31_test_evidence_truthfulness_contract")
    git = v31_json(paths, "v31_git_diff_evidence_pack")
    checksum = v31_json(paths, "v31_artifact_checksum_provenance_pack")
    external = v31_json(paths, "v31_external_reviewer_audit_package_result")

    assert truth["fabricated_test_result"] is False
    assert truth["timeout_transparency_warning"] is False
    assert "partial_result_labeled_full" in truth["disallowed_test_evidence_types"]
    assert git["semantic_fix_commit_verified"] is True
    assert git["fabricated_git_evidence"] is False
    assert all(record["exists"] for record in git["file_level_change_evidence"])
    assert checksum["artifact_checksum_provenance_pack_generated"] is True
    assert checksum["fabricated_checksum"] is False
    assert external["external_reviewer_audit_package_generated"] is True
    assert external["broker_setup_included"] is False


def test_v31_artifact_inventory_and_markdown_names(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    data_dir = paths.data_dir / "equity_v31_post_v3_verification" / "daily" / DEFAULT_AS_OF_DATE
    output_dir = paths.outputs_dir / "equity_v31_post_v3_verification" / "daily" / DEFAULT_AS_OF_DATE

    assert len(JSON_NAMES) == 16
    assert len(MARKDOWN_NAMES) == 11
    assert all((data_dir / f"{name}.json").exists() for name in JSON_NAMES)
    assert all((output_dir / name).exists() for name in MARKDOWN_NAMES)
    assert (output_dir / "A_SHARE_V31_SPLIT_MATRIX_FULL_REGRESSION_EVIDENCE.md").exists()
    assert (output_dir / "A_SHARE_V31_GIT_DIFF_EVIDENCE_PACK.md").exists()


def test_v31_audit_enforces_required_true_false_and_boundaries(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    audit = audit_a_share_v31_post_v3_verification(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["artifact_checks"]["all_json_present"] is True
    assert audit["artifact_checks"]["all_markdown_present"] is True
    evidence = v31_json(paths, "v31_full_regression_command_evidence")
    assert audit["full_regression_total_passed"] == evidence["summary"]["passed"]
    assert audit["full_regression_total_skipped"] == evidence["summary"]["skipped"]
    assert all(value is True for value in audit["quality_checks"].values())
    assert all(value is False for value in audit["forbidden_checks"].values())

    result = v31_json(paths, "v31_post_v3_verification_result")
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False


def test_v31_requires_simulation_only(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    result = run_a_share_v31_post_v3_verification(paths=paths)

    assert result["overall_passed"] is False
    assert result["blocking_reasons"] == ["simulation_only_flag_required"]


def test_v31_audit_rejects_tampered_raw_pytest_output(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    evidence = v31_json(paths, "v31_full_regression_command_evidence")
    Path(evidence["raw_stdout_path"]).write_text("=== 1 failed in 0.01s ===\n", encoding="utf-8")

    audit = audit_a_share_v31_post_v3_verification(paths=paths)

    assert audit["overall_passed"] is False
    assert "full regression stdout checksum mismatch" in audit["blocking_reasons"]
    assert "full regression parsed raw output does not match evidence summary" in audit["blocking_reasons"]


def test_v31_audit_rejects_stale_or_mismatched_command_evidence(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    evidence = v31_json(paths, "v31_full_regression_command_evidence")
    evidence["summary"] = {**evidence["summary"], "passed": evidence["summary"]["passed"] + 1}
    write_v31_json(paths, "v31_full_regression_command_evidence", evidence)

    audit = audit_a_share_v31_post_v3_verification(paths=paths)

    assert audit["overall_passed"] is False
    assert "full regression parsed raw output does not match evidence summary" in audit["blocking_reasons"]
    assert "full_regression_totals_do_not_match_command_evidence" in audit["blocking_reasons"]


def test_v31_audit_rejects_missing_semantic_source_references(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    semantic = v31_json(paths, "v31_semantic_regression_pack_result")
    semantic["source_evidence_references"].pop("t_plus_one_dated_settlement_verified")
    write_v31_json(paths, "v31_semantic_regression_pack_result", semantic)

    audit = audit_a_share_v31_post_v3_verification(paths=paths)

    assert audit["overall_passed"] is False
    assert "semantic_source_evidence_reference_missing:t_plus_one_dated_settlement_verified" in audit["blocking_reasons"]


def test_v31_audit_rejects_manifest_content_and_envelope_drift(tmp_path: Path) -> None:
    paths = make_v31_paths(tmp_path)
    run_a_share_v31_post_v3_verification(paths=paths, simulation_only=True)
    semantic = v31_json(paths, "v31_semantic_regression_pack_result")
    semantic["warnings"] = ["tampered-after-manifest"]
    write_v31_json(paths, "v31_semantic_regression_pack_result", semantic)

    audit = audit_a_share_v31_post_v3_verification(paths=paths)

    assert audit["overall_passed"] is False
    assert "manifest_envelope_checksum_mismatch:v31_semantic_regression_pack_result" in audit["blocking_reasons"]
    assert "manifest_content_checksum_mismatch:v31_semantic_regression_pack_result" in audit["blocking_reasons"]


def test_v31_cli_build_audit_and_component_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from trading_core import cli

    paths = make_v31_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    artifact_dir = tmp_path / "v31-artifacts"
    assert cli.main(["build-a-share-v31-post-v3-verification", "--as-of-date", DEFAULT_AS_OF_DATE, "--simulation-only", "--output-dir", str(artifact_dir)]) == 0
    assert "overall_passed" in capsys.readouterr().out
    for command in [
        "build-a-share-v31-semantic-regression-pack",
        "build-a-share-v31-split-matrix-evidence",
        "build-a-share-v31-test-evidence-contract",
        "build-a-share-v31-git-evidence-pack",
        "build-a-share-v31-artifact-checksum-pack",
        "build-a-share-v31-external-audit-package",
        "build-a-share-v31-owner-verification-dashboard",
    ]:
        assert cli.main([command, "--as-of-date", DEFAULT_AS_OF_DATE, "--simulation-only", "--output-dir", str(artifact_dir)]) == 0
        assert "overall_passed" in capsys.readouterr().out

    assert cli.main(["audit-a-share-v31-post-v3-verification", "--as-of-date", DEFAULT_AS_OF_DATE, "--input-dir", str(artifact_dir)]) == 0
    assert "overall_passed" in capsys.readouterr().out
    assert cli.main(["build-and-audit-a-share-v31-post-v3-verification", "--as-of-date", DEFAULT_AS_OF_DATE, "--simulation-only", "--output-dir", str(artifact_dir)]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out


def test_v31_cli_rejects_unsafe_output_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v31_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v31-post-v3-verification", "--as-of-date", DEFAULT_AS_OF_DATE, "--simulation-only", "--output-dir", str(paths.project_root / "src")]) == 2
