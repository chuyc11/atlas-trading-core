from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.status_brief import build_status_brief


def test_owner_daily_status_brief_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    brief = build_status_brief(paths=paths, as_of_date=AS_OF_DATE)

    assert brief["brief_id"] == "A-SHARE-OWNER-DAILY-STATUS-BRIEF"
    assert brief["overall_status"] == "passed_with_warnings"
    assert brief["automatic_action_count"] == 0
    assert brief["not_trade_instruction"] is True
