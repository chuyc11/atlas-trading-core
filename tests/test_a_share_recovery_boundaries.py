from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, recovery_data, seed_owner_readiness_recovery_outputs
from trading_core.equity_owner_readiness_recovery.recovery_boundary import build_boundary_check


def test_a_share_recovery_boundaries_block_forbidden_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    report_dir = paths.outputs_dir / "equity_owner_readiness_recovery" / "daily" / AS_OF_DATE
    (report_dir / "BAD.md").write_text("买入建议", encoding="utf-8")
    boundary = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE)
    assert boundary["overall_passed"] is False
    assert boundary["forbidden_wording_positive_hits"]


def test_a_share_recovery_boundaries_preserve_no_execution_flags(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    boundary = recovery_data(paths, "recovery_boundary_check.json")
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["execute_remediation_actions"] is False
    assert boundary["order_preview_generated"] is False
