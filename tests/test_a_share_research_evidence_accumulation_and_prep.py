from __future__ import annotations

from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_a, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_build_generates_phase_a_evidence_register_and_result(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)

    result = build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    register = phase_a(paths, "evidence_eligible_day_register")
    assert result["overall_passed"] is True
    assert register["eligible_day_count"] == 2
    assert register["prep_evidence_day_count_passed"] is True
    assert register["controlled_reevaluation_day_count_passed"] is False
    assert register["planned_but_not_evidence_days"] == []


def test_source_inventory_records_artifact_hashes(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    inventory = phase_a(paths, "source_artifact_inventory")

    assert inventory["artifact_count"] > 0
    assert any(item["sha256"] for item in inventory["artifacts"] if item["exists"])
    assert inventory["v093_data_freshness_present"] is True
    assert inventory["v094_research_pipeline_rerun_present"] is True


def test_missing_outputs_are_ineligible_not_fabricated(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    (paths.data_dir / "equity_briefings" / "daily" / "2026-06-26" / "briefing_manifest.json").unlink()

    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)
    register = phase_a(paths, "evidence_eligible_day_register")

    assert register["eligible_day_count"] == 1
    assert [item["date"] for item in register["ineligible_days"]] == ["2026-06-26"]
    assert "2026-06-27" not in [item["date"] for item in register["eligible_days"]]


def test_candidate_score_portfolio_briefing_boundary_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    candidate = phase_a(paths, "candidate_overlap_and_turnover_diagnostics")
    score = phase_a(paths, "score_distribution_diagnostics")
    portfolio = phase_a(paths, "virtual_portfolio_research_diagnostics")
    briefing = phase_a(paths, "research_briefing_quality_diagnostics")
    boundary = phase_a(paths, "research_only_boundary_validation")

    assert candidate["forbidden_wording_present"] is False
    assert "added_to_research_candidate_set" in candidate["candidate_label_policy"]
    assert score["not_trade_signal"] is True
    assert score["not_owner_readiness_score"] is True
    assert "research_score != buy/sell signal" in score["score_boundary_statements"]
    assert portfolio["virtual_only"] is True
    assert portfolio["not_real_portfolio"] is True
    assert briefing["not_investment_advice"] is True
    assert boundary["research_only_boundary_validation_passed"] is True
    assert boundary["owner_readiness_gate_rerun"] is False
    assert boundary["new_gate_score_generated"] is False


def test_evidence_accumulation_result_is_prep_only(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    result = phase_a(paths, "evidence_accumulation_result")

    assert result["evidence_accumulation_status"] == "sufficient_for_prep"
    assert result["data_refresh_run"] is False
    assert result["research_pipeline_rerun_run"] is False
    assert result["build_from_existing_data_run"] is False
    assert result["owner_readiness_gate_rerun"] is False
    assert result["new_gate_decision_generated"] is False
