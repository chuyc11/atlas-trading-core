from tests.a_share_ops_history_test_utils import build_ops_history_artifacts
from tests.a_share_owner_dashboard_test_utils import make_paths


def test_ops_history_boundaries_remain_research_only(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_ops_history_artifacts(paths)
    boundary = audit["boundary"]
    assert boundary["ops_history_only"] is True
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["real_orders_placed"] is False
