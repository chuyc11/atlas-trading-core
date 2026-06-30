from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_exception_audit_trail_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    trail = exception_data(paths, "exception_audit_trail.json")
    assert trail["owner_notice_generated"] is True
    assert trail["external_notifications_sent"] is False
