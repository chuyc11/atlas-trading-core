from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_inputs
from trading_core.equity_owner_evidence_backed_reevaluation_prep.input_availability import build_input_availability
from trading_core.equity_owner_evidence_backed_reevaluation_prep.source_resolution import build_source_resolution


def test_evidence_backed_prep_source_resolution_prefers_recovery_evidence(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.8.18_recovery_evidence_artifacts"
    assert resolution["no_broker_inputs"] is True

