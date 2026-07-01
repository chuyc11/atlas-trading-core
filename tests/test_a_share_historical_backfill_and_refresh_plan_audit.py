from tests.a_share_historical_backfill_test_utils import build_v097, seed_v096_with_historical_inputs
from trading_core.equity_historical_evidence_backfill import audit_a_share_historical_evidence_backfill_and_refresh_plan


def test_historical_backfill_and_refresh_plan_audit_passes_with_honest_shortfall(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    build_v097(paths, monkeypatch)

    audit = audit_a_share_historical_evidence_backfill_and_refresh_plan(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["artifact_checks"]["target_evidence_count_not_fabricated"] is True
    assert audit["boundary"]["owner_readiness_gate_rerun"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["refresh_checks"]["post_close_plan_does_not_install_scheduler"] is True
    assert audit["test_policy"]["full_pytest_run"] is False
