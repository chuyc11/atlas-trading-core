from tests.a_share_research_evidence_test_utils import AS_OF_DATE
from trading_core.cli import build_parser, main


def test_historical_backfill_cli_commands_registered():
    parser = build_parser()

    assert parser.parse_args(["build-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]).command == "build-a-share-historical-evidence-backfill-and-refresh-plan"
    assert parser.parse_args(["audit-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]).command == "audit-a-share-historical-evidence-backfill-and-refresh-plan"
    assert parser.parse_args(["build-and-audit-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]).command == "build-and-audit-a-share-historical-evidence-backfill-and-refresh-plan"


def test_historical_backfill_cli_build_audit_smoke(monkeypatch, capsys):
    import trading_core.cli as cli

    build_payload = {
        "builder_id": "A-SHARE-HISTORICAL-EVIDENCE-BACKFILL-AND-REFRESH-PLAN",
        "target_version": "v0.9.7-a-share-historical-evidence-backfill-and-post-close-refresh-planning",
        "as_of_date": AS_OF_DATE,
        "lookback_start": "2026-06-19",
        "historical_window_end": AS_OF_DATE,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "v096_baseline_verified": True,
        "resolved_trading_days": ["2026-06-25", "2026-06-26", "2026-07-01"],
        "existing_eligible_days": ["2026-06-26", "2026-07-01"],
        "selected_backfill_days": ["2026-06-25"],
        "backfilled_days": [],
        "failed_backfill_days": ["2026-06-25"],
        "eligible_day_count_after_backfill": 2,
        "target_total_evidence_days": 5,
        "target_total_evidence_days_passed": False,
        "research_output_completeness_passed": True,
        "evidence_quality_overall_status": "partial",
        "blocker_coverage_ratio": 0.5,
        "prep_coverage_passed": False,
        "controlled_reevaluation_coverage_passed": False,
        "ready_for_future_controlled_reevaluation_prep": False,
        "go_no_go_after_backfill_decision": "no_go_additional_evidence_required",
        "post_close_refresh_plan_generated": True,
        "post_close_refresh_recommended_time": "15:45",
        "post_close_refresh_timezone": "Asia/Shanghai",
        "post_close_refresh_public_data_only": True,
        "post_close_refresh_installs_scheduler": False,
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "public_network_refresh_run": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "recommended_next_version": "v0.9.8-a-share-reevaluation-readiness-closeout-after-backfill",
    }
    audit_payload = {
        "audit_id": "A-SHARE-HISTORICAL-BACKFILL-AND-REFRESH-PLANNING-AUDIT",
        "target_version": build_payload["target_version"],
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "artifact_checks": {},
        "boundary": {},
        "refresh_checks": {},
        "readiness_checks": {},
        "go_no_go_after_backfill_decision": "no_go_additional_evidence_required",
    }
    monkeypatch.setattr(cli, "build_a_share_historical_evidence_backfill_and_refresh_plan", lambda **_: build_payload)
    monkeypatch.setattr(cli, "audit_a_share_historical_evidence_backfill_and_refresh_plan", lambda **_: audit_payload)

    assert main(["build-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]) == 0
    assert "no_go_additional_evidence_required" in capsys.readouterr().out
    assert main(["audit-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-HISTORICAL-BACKFILL-AND-REFRESH-PLANNING-AUDIT" in capsys.readouterr().out
    assert main(["build-and-audit-a-share-historical-evidence-backfill-and-refresh-plan", "--as-of-date", AS_OF_DATE]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
