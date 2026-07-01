from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_blocker_mapping_preserves_thresholds_without_lowering(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    mapping = phase_b(paths, "blocker_evidence_mapping")

    assert mapping["source_owner_readiness_state"] == "blocked"
    assert mapping["source_readiness_score"] == 54
    assert mapping["minimum_owner_readiness_score"] == 75
    assert mapping["minimum_blocker_coverage_ratio_for_prep"] == 0.6
    assert mapping["minimum_blocker_coverage_ratio_for_controlled_reevaluation"] == 0.85
    assert mapping["controlled_reevaluation_coverage_passed"] is False
