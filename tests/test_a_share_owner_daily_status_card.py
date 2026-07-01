from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_owner_daily_status_card_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    card = operator_data(paths, "owner_daily_status_card.json")
    assert card["system_state"] == "research_system_rc_passed"
    assert card["owner_readiness_state"] == "blocked"
    assert card["live_trading_ready"] is False
