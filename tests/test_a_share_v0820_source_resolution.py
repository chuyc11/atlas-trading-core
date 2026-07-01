from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_inputs
from trading_core.equity_owner_v0820_gate_outcome.input_availability import build_input_availability
from trading_core.equity_owner_v0820_gate_outcome.source_resolution import build_source_resolution


def test_v0820_source_resolution_prefers_v0819_prep(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.8.19_evidence_backed_prep_artifacts"
    assert resolution["no_real_account_inputs"] is True

