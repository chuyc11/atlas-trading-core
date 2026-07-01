from tests.a_share_historical_backfill_test_utils import build_v097, refresh_json, seed_v096_with_historical_inputs


def test_post_close_refresh_plan_is_public_data_only_and_does_not_install_scheduler(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    build_v097(paths, monkeypatch)
    plan = refresh_json(paths, "post_close_refresh_plan")
    command_plan = refresh_json(paths, "post_close_refresh_command_plan")
    boundary = refresh_json(paths, "post_close_refresh_safety_boundary")
    schedule = refresh_json(paths, "post_close_refresh_schedule_recommendation")

    assert plan["timezone"] == "Asia/Shanghai"
    assert plan["recommended_run_time"] == "15:45"
    assert plan["public_market_data_only"] is True
    assert {"broker", "orders", "buy_sell_signals", "owner_readiness_gate", "controlled_reevaluation"}.issubset(set(plan["explicitly_excluded_scope"]))
    assert command_plan["commands_executed_by_this_version"] == []
    assert boundary["installs_scheduler"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert schedule["installs_windows_task_scheduler_entry"] is False
    assert schedule["installs_cron_entry"] is False
