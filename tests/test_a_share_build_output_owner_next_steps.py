from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from tests.a_share_owner_dashboard_test_utils import write_json
from trading_core.equity_build_output_ops_refresh.owner_next_steps import build_owner_next_steps_refresh


def test_build_output_owner_next_steps_exclude_trade_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    target = paths.data_dir / "equity_ops_center" / "daily" / AS_OF_DATE / "ops_owner_next_steps.json"
    write_json(target, {"review_today": ["检查 audit 是否通过", "连接 broker 做实盘"], "do_now": [], "wait_for_more_history": [], "developer_follow_up": [], "no_action_required": []})
    result = build_owner_next_steps_refresh(paths=paths, as_of_date=AS_OF_DATE)
    assert "检查 audit 是否通过" in result["review_today"]
    assert result["excluded_trade_action_steps"] == ["连接 broker 做实盘"]
    assert result["overall_passed"] is False

