from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day.current_day_boundary import build_current_day_boundary_check
from trading_core.equity_current_day.workflow_plan import build_current_day_workflow_plan


def test_current_day_boundaries_no_broker_orders_or_signals(tmp_path):
    paths = make_paths(tmp_path)
    plan = build_current_day_workflow_plan(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, workflow_mode="validate_existing_artifacts")
    boundary = build_current_day_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert "run-daily" not in plan["workflow_command"]
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["real_account_data_read"] is False
    assert boundary["research_result_used_as_trade_instruction"] is False

