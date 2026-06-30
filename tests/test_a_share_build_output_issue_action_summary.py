from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.issue_action_summary import build_action_summary_refresh, build_issue_summary_refresh
from trading_core.equity_build_output_ops_refresh.remediation_refresh import build_safe_action_refresh


def test_build_output_issue_and_action_summary_refresh(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    issue = build_issue_summary_refresh(paths=paths, as_of_date=AS_OF_DATE)
    safe = build_safe_action_refresh(paths=paths, as_of_date=AS_OF_DATE)
    action = build_action_summary_refresh(paths=paths, as_of_date=AS_OF_DATE, safe_action_refresh=safe)
    assert issue["issue_summary_refresh_performed"] is True
    assert action["action_summary_refresh_performed"] is True
    assert action["automatic_action_count"] == 0

