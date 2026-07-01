from tests.a_share_historical_backfill_test_utils import build_v097, historical_json, seed_v096_with_historical_inputs


def test_historical_backfill_records_failed_days_without_fabricating_target(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    result = build_v097(paths, monkeypatch)
    backfill = historical_json(paths, "historical_research_backfill_result")

    assert result["overall_passed"] is True
    assert backfill["selected_backfill_days"] == ["2026-06-25", "2026-06-24", "2026-06-23", "2026-06-22"]
    assert backfill["backfilled_days"] == []
    assert backfill["failed_backfill_days"] == ["2026-06-25", "2026-06-24", "2026-06-23", "2026-06-22"]
    assert backfill["eligible_day_count_after_backfill"] == 2
    assert backfill["target_total_evidence_days_passed"] is False
    assert backfill["target_count_not_fabricated"] is True
    assert backfill["public_network_refresh_run"] is False
    assert backfill["owner_readiness_gate_rerun"] is False
    assert backfill["new_gate_score_generated"] is False
    assert backfill["buy_sell_signals_generated"] is False


def test_historical_backfill_can_count_successful_research_only_days(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    result = build_v097(paths, monkeypatch, successful_days=["2026-06-25", "2026-06-24", "2026-06-23"])

    assert result["backfilled_days"] == ["2026-06-25", "2026-06-24", "2026-06-23"]
    assert result["eligible_day_count_after_backfill"] == 5
    assert result["target_total_evidence_days_passed"] is True
    assert result["owner_readiness_gate_rerun"] is False
