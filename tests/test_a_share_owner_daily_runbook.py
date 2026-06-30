from tests.a_share_build_output_ops_test_utils import AS_OF_DATE
from trading_core.equity_owner_daily_pack.daily_runbook import build_daily_runbook


def test_owner_daily_runbook_generated_with_safe_audit_commands():
    runbook = build_daily_runbook(as_of_date=AS_OF_DATE)

    assert runbook["runbook_id"] == "A-SHARE-OWNER-DAILY-RUNBOOK"
    assert "打开每日状态简报" in runbook["sections"]
    assert "确认不执行任何交易动作" in runbook["sections"]
    assert runbook["commands_executed"] == []
    assert all("audit-a-share" in command for command in runbook["safe_audit_only_commands"])
