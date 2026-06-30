from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.health_score_refresh import build_health_score_refresh


def test_build_output_health_score_refresh_deterministic(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    first = build_health_score_refresh(paths=paths, as_of_date=AS_OF_DATE)
    second = build_health_score_refresh(paths=paths, as_of_date=AS_OF_DATE)
    assert first == second
    assert first["score"] == 65
    assert first["grade"] == "C"

