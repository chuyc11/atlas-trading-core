from __future__ import annotations

import json

from tests.a_share_v09_platform_test_utils import AS_OF_DATE, make_paths, read_json
from trading_core.equity_v100_release import audit_a_share_v100_release, build_a_share_v100_release
from trading_core.equity_v100_release import builder as release_builder


def test_v100_release_builds_final_decision_and_audit(monkeypatch, tmp_path):
    paths = make_paths(tmp_path)
    monkeypatch.setattr(release_builder, "_prep_verification", lambda *_args, **_kwargs: _prep_verified())

    result = build_a_share_v100_release(as_of_date=AS_OF_DATE, paths=paths)
    assert result["overall_passed"] is True
    assert result["final_release_decision"] == "released_as_research_only_simulation_platform"
    assert result["platform_scope"] == "research_only_simulation_only_autonomous_research_platform"
    assert result["known_limitations_count"] == 8
    assert result["full_pytest_reused_from_v100_prep"] is True
    assert result["full_pytest_rerun"] is False
    assert result["owner_readiness_state"] == "blocked"
    assert result["live_trading_ready"] is False

    decision = read_json(paths.data_dir / "equity_v100_release" / "daily" / AS_OF_DATE / "v100_final_release_decision.json")
    assert decision["warnings"] == []
    assert decision["blocking_warning_count"] == 0
    assert decision["not_real_trading_system"] is True

    limitations = read_json(paths.data_dir / "equity_v100_release" / "daily" / AS_OF_DATE / "v100_known_limitations_register.json")
    assert limitations["known_limitations_count"] == 8
    assert limitations["benchmark_warning_blocks_real_performance_claims"] is True

    audit = audit_a_share_v100_release(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["known_limitations_count"] == 8


def test_v100_release_audit_fails_closed_on_real_order_boundary(monkeypatch, tmp_path):
    paths = make_paths(tmp_path)
    monkeypatch.setattr(release_builder, "_prep_verification", lambda *_args, **_kwargs: _prep_verified())
    build_a_share_v100_release(as_of_date=AS_OF_DATE, paths=paths)

    decision_path = paths.data_dir / "equity_v100_release" / "daily" / AS_OF_DATE / "v100_final_release_decision.json"
    decision = read_json(decision_path)
    decision["real_orders_placed"] = True
    decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    audit = audit_a_share_v100_release(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert "forbidden_boundary_true:real_orders_placed" in audit["blocking_reasons"]


def _prep_verified():
    return {
        "verification_id": "A-SHARE-V100-PREP-VERIFICATION",
        "v100_prep_verified": True,
        "release_readiness_decision_ready": True,
        "release_readiness_decision_from_prep": "ready_for_v100_release",
        "full_regression_passed": True,
        "full_regression_result": "1807 passed, 1 skipped, 0 failed",
        "full_regression_duration_seconds": 846.103,
        "full_pytest_reused_from_v100_prep": True,
        "full_pytest_rerun": False,
        "blocking_warning_count": 0,
        "benchmark_warning_classification": "non_blocking_for_research_only_simulation_release_blocks_real_performance_claims",
        "safety_boundary_sweep_passed": True,
        "artifact_integrity_passed": True,
        "cli_surface_verified": True,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "waiver_applied": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "real_order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "silent_scheduler_installed": False,
        "daemon_installed": False,
        "blocking_reasons": [],
    }
