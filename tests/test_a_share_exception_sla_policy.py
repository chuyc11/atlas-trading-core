from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_exception_sla_policy_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    sla = exception_data(paths, "exception_sla_policy.json")
    assert sla["sla_hours"]["blocking"] == 24
    assert sla["external_notifications_sent"] is False
