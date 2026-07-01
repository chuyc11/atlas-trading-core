from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_inputs
from trading_core.equity_owner_v090_rc.input_availability import build_input_availability
from trading_core.equity_owner_v090_rc.source_resolution import build_source_resolution


def test_v090_source_resolution_prefers_v0821_closeout(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.8.21_closeout_review_artifacts"
    assert resolution["no_real_account_inputs"] is True
