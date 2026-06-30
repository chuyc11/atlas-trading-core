from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json
from trading_core.equity_owner_daily_pack_history.readiness_score import grade_for_score


def test_owner_readiness_score_deterministic(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    score = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "owner_readiness_score.json")
    assert score["score"] == 95
    assert score["grade"] == "A"
    assert score["owner_readiness_used_as_trade_instruction"] is False


def test_owner_readiness_grade_mapping():
    assert grade_for_score(95) == "A"
    assert grade_for_score(80) == "B"
    assert grade_for_score(65) == "C"
    assert grade_for_score(45) == "D"
    assert grade_for_score(20) == "F"
