from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.warning_issue_digest import build_warning_issue_digest


def test_warning_issue_digest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_warning_issue_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["digest_id"] == "A-SHARE-WARNING-ISSUE-DIGEST"
    assert digest["blocking_count"] == 0
    assert digest["warning_count"] >= 1
    assert digest["not_trade_instruction"] is True
