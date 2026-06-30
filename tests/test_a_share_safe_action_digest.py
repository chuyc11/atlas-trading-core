from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from tests.a_share_owner_dashboard_test_utils import write_json
from trading_core.equity_owner_daily_pack.safe_action_digest import build_safe_action_digest


def test_safe_action_digest_has_zero_automatic_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_safe_action_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["automatic_action_count"] == 0
    assert digest["execute_remediation_actions"] is False
    assert digest["overall_passed"] is True


def test_safe_action_digest_blocks_forbidden_action_type(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    path = paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_safe_action_refresh.json"
    write_json(
        path,
        {
            "target_version": "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh",
            "as_of_date": AS_OF_DATE,
            "items": [{"item_id": "bad", "safe_action_type": "place_order", "allowed_to_execute_automatically": False}],
        },
    )

    digest = build_safe_action_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["overall_passed"] is False
    assert digest["forbidden_safe_action_type_hits"] == ["bad"]
