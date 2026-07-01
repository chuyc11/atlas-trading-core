from tests.a_share_v09_platform_test_utils import AS_OF_DATE
from trading_core.cli import build_parser, main


def test_v100_release_cli_commands_registered():
    parser = build_parser()
    for command in ["build-a-share-v100-release", "audit-a-share-v100-release", "build-and-audit-a-share-v100-release"]:
        assert parser.parse_args([command, "--as-of-date", AS_OF_DATE]).command == command


def test_v100_release_cli_smoke(monkeypatch, capsys):
    import trading_core.cli as cli

    build = {
        "builder_id": "A-SHARE-V100-FINAL-RELEASE",
        "target_version": "v1.0.0-a-share-autonomous-simulation-platform-release",
        "source_version": "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout",
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "final_release_decision": "released_as_research_only_simulation_platform",
        "platform_scope": "research_only_simulation_only_autonomous_research_platform",
        "blocking_reasons": [],
        "warnings": [],
        "v100_prep_verified": True,
        "release_readiness_decision_from_prep": "ready_for_v100_release",
        "full_regression_passed": True,
        "full_regression_result": "1807 passed, 1 skipped, 0 failed",
        "full_pytest_reused_from_v100_prep": True,
        "full_pytest_rerun": False,
        "blocking_warning_count": 0,
        "benchmark_warning_classification": "non_blocking",
        "safety_boundary_sweep_passed": True,
        "artifact_integrity_passed": True,
        "cli_surface_verified": True,
        "known_limitations_count": 8,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "real_order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "recommended_next_version": "v1.0.1-a-share-benchmark-data-and-performance-claim-hardening",
    }
    audit = {
        "audit_id": "A-SHARE-V100-RELEASE-AUDIT",
        "target_version": build["target_version"],
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "artifact_checks": {},
        "release_decision": {},
        "owner_readiness": {},
        "boundary": {},
        "known_limitations_count": 8,
        "recommended_next_version": build["recommended_next_version"],
    }
    monkeypatch.setattr(cli, "build_a_share_v100_release", lambda **_: build)
    monkeypatch.setattr(cli, "audit_a_share_v100_release", lambda **_: audit)

    assert main(["build-a-share-v100-release", "--as-of-date", AS_OF_DATE]) == 0
    assert "released_as_research_only_simulation_platform" in capsys.readouterr().out
    assert main(["audit-a-share-v100-release", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-V100-RELEASE-AUDIT" in capsys.readouterr().out
    assert main(["build-and-audit-a-share-v100-release", "--as-of-date", AS_OF_DATE]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
