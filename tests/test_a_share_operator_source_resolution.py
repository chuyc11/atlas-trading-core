from tests.a_share_operator_experience_test_utils import make_paths, seed_operator_inputs
from trading_core.equity_owner_operator_experience.input_availability import build_input_availability
from trading_core.equity_owner_operator_experience.source_resolution import build_source_resolution


def test_operator_source_resolution_prefers_v090_rc(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_inputs(paths)
    availability = build_input_availability(paths=paths)
    resolution = build_source_resolution(paths=paths, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.9.0_rc_artifacts"
