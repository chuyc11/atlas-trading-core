from tests.a_share_v09_platform_test_utils import AS_OF_DATE
from trading_core.cli import build_parser, main


def test_v100_prep_cli_commands_registered():
    parser = build_parser()
    for command in ["build-a-share-v100-prep", "audit-a-share-v100-prep", "build-and-audit-a-share-v100-prep"]:
        assert parser.parse_args([command, "--as-of-date", AS_OF_DATE]).command == command


def test_v100_prep_cli_smoke(monkeypatch, capsys):
    import trading_core.cli as cli

    build = {
        "builder_id": "A-SHARE-V100-PREP-CLOSEOUT",
        "target_version": "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout",
        "source_version": "v0.9.8-a-share-v09-autonomous-research-and-simulation-platform-completion",
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "release_readiness_decision": "ready_for_v100_release",
        "blocking_reasons": [],
        "warnings": [{}, {}],
        "v098_platform_verified": True,
        "v098_warnings_count": 2,
        "blocking_warning_count": 0,
        "full_regression_passed": True,
        "full_pytest_passed_count": 10,
        "full_pytest_skipped_count": 1,
        "full_pytest_failed_count": 0,
        "full_pytest_duration_seconds": 1.23,
        "cli_surface_verified": True,
        "artifact_integrity_passed": True,
        "safety_boundary_sweep_passed": True,
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
        "recommended_next_version": "v1.0.0-a-share-autonomous-simulation-platform-release",
    }
    audit = {
        "audit_id": "A-SHARE-V100-PREP-AUDIT",
        "target_version": build["target_version"],
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [{}, {}],
        "artifact_checks": {},
        "readiness_decision": {},
        "owner_readiness": {},
        "boundary": {},
        "recommended_next_version": build["recommended_next_version"],
    }
    monkeypatch.setattr(cli, "build_a_share_v100_prep", lambda **_: build)
    monkeypatch.setattr(cli, "audit_a_share_v100_prep", lambda **_: audit)

    assert main(["build-a-share-v100-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "ready_for_v100_release" in capsys.readouterr().out
    assert main(["audit-a-share-v100-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-V100-PREP-AUDIT" in capsys.readouterr().out
    assert main(["build-and-audit-a-share-v100-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
