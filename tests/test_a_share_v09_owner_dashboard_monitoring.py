from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_v09_daily_platform


def test_v09_owner_dashboard_and_monitoring_are_local_artifacts(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    dashboard = platform_json(paths, "v09_owner_dashboard_result")
    monitoring = platform_json(paths, "v09_monitoring_alerts_result")

    assert "不是投资建议" in dashboard["plain_language_notice"]
    assert "不是真实订单" in dashboard["plain_language_notice"]
    assert "不能复制到真实账户执行" in dashboard["plain_language_notice"]
    assert dashboard["owner_readiness_status"] == "blocked"
    assert monitoring["external_notification_sent"] is False
    assert all(alert["not_buy_sell_signal"] for alert in monitoring["alerts"])
