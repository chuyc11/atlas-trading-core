from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from tests.a_share_owner_dashboard_test_utils import write_json
from trading_core.equity_build_output_ops_refresh.remediation_refresh import build_remediation_refresh, build_safe_action_refresh


def test_build_output_remediation_and_safe_action_refresh(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    remediation = build_remediation_refresh(paths=paths, as_of_date=AS_OF_DATE)
    safe = build_safe_action_refresh(paths=paths, as_of_date=AS_OF_DATE)
    assert remediation["execute_remediation_actions"] is False
    assert safe["automatic_action_count"] == 0
    assert safe["overall_passed"] is True
    checklist = paths.data_dir / "equity_owner_remediation" / "daily" / AS_OF_DATE / "safe_owner_action_checklist.json"
    write_json(checklist, {"items": [{"item_id": "BAD", "safe_action_type": "place_order", "allowed_to_execute_automatically": True}]})
    failed = build_safe_action_refresh(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False

