from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_manual_waiver_policy_default_not_approved(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    record = exception_data(paths, "manual_waiver_decision_record.json")
    policy = exception_data(paths, "manual_waiver_policy.json")
    assert record["manual_waiver_decision_status"] == "not_requested"
    assert record["manual_waiver_approval_recorded"] is False
    assert policy["cannot_authorize_trading"] is True
