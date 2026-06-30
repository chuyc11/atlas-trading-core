from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from tests.a_share_owner_dashboard_test_utils import write_json
from trading_core.equity_owner_daily_pack.next_step_checklist import build_next_step_checklist


def test_owner_next_step_checklist_excludes_trade_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    path = paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_owner_next_steps_refresh.json"
    write_json(
        path,
        {
            "target_version": "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh",
            "as_of_date": AS_OF_DATE,
            "do_now": ["connect broker and place order"],
            "review_today": ["检查 audit 是否通过"],
            "wait_for_more_history": [],
            "developer_follow_up": [],
            "no_action_required": [],
        },
    )

    checklist = build_next_step_checklist(paths=paths, as_of_date=AS_OF_DATE)

    assert checklist["do_now"] == []
    assert checklist["excluded_trade_action_steps"] == ["connect broker and place order"]
