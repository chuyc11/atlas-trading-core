from tests.a_share_evidence_backed_prep_test_utils import make_paths, seed_evidence_backed_prep_outputs, prep_data


def test_evidence_backed_prep_boundary_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_outputs(paths)
    boundary = prep_data(paths, "evidence_backed_prep_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
    assert boundary["old_run_daily_called"] is False
    assert boundary["evidence_backed_prep_used_as_trade_instruction"] is False

