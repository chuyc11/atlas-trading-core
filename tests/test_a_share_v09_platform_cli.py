from tests.a_share_v09_platform_test_utils import AS_OF_DATE
from trading_core.cli import build_parser, main


def test_v09_platform_cli_commands_registered():
    parser = build_parser()
    commands = [
        "run-a-share-v09-daily-platform",
        "audit-a-share-v09-platform",
        "run-and-audit-a-share-v09-platform",
        "build-a-share-experiment-registry",
        "run-a-share-automated-experiments",
        "run-a-share-rl-simulated-strategy-lab",
        "evaluate-a-share-simulated-strategy-promotion",
    ]
    for command in commands:
        assert parser.parse_args([command, "--as-of-date", AS_OF_DATE]).command == command


def test_v09_platform_cli_smoke(monkeypatch, capsys):
    import trading_core.cli as cli

    base = {
        "builder_id": "A-SHARE-V09-DAILY-PLATFORM",
        "target_version": "v0.9.8-a-share-v09-autonomous-research-and-simulation-platform-completion",
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "run_status": "passed",
        "dry_run": False,
        "blocking_reasons": [],
        "warnings": [],
        "public_data_refresh_status": "passed",
        "research_pipeline_status": "passed",
        "simulated_account_updated": True,
        "virtual_broker_execution_run": True,
        "paper_ledger_updated": True,
        "benchmark_attribution_status": "warning",
        "owner_dashboard_generated": True,
        "monitoring_alerts_generated": True,
        "evidence_auto_accumulation_run": True,
        "experiment_registry_generated": True,
        "strategy_registry_generated": True,
        "llm_research_proposals_generated": True,
        "automated_experiments_run": True,
        "rl_simulated_strategy_lab_run": True,
        "shadow_canary_promotion_evaluated": True,
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
        "protected_paths_untouched": True,
        "recommended_next_version": "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout",
    }
    audit = {"audit_id": "A-SHARE-V09-PLATFORM-COMPLETION-AUDIT", "target_version": base["target_version"], "as_of_date": AS_OF_DATE, "overall_passed": True, "blocking_reasons": [], "warnings": [], "artifact_checks": {}, "boundary": {}, "workflow": {}}
    monkeypatch.setattr(cli, "run_a_share_v09_daily_platform", lambda **_: base)
    monkeypatch.setattr(cli, "audit_a_share_v09_platform", lambda **_: audit)
    monkeypatch.setattr(cli, "build_a_share_experiment_registry", lambda **_: {"overall_passed": True})
    monkeypatch.setattr(cli, "run_a_share_automated_experiments", lambda **_: {"overall_passed": True})
    monkeypatch.setattr(cli, "run_a_share_rl_simulated_strategy_lab", lambda **_: {"overall_passed": True})
    monkeypatch.setattr(cli, "evaluate_a_share_simulated_strategy_promotion", lambda **_: {"overall_passed": True})

    assert main(["run-a-share-v09-daily-platform", "--as-of-date", AS_OF_DATE, "--simulation-only"]) == 0
    assert "A-SHARE-V09-DAILY-PLATFORM" in capsys.readouterr().out
    assert main(["audit-a-share-v09-platform", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-V09-PLATFORM-COMPLETION-AUDIT" in capsys.readouterr().out
    assert main(["run-and-audit-a-share-v09-platform", "--as-of-date", AS_OF_DATE, "--simulation-only"]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
