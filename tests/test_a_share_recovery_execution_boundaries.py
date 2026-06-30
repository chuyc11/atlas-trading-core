from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, execution_data, seed_recovery_execution_outputs
from trading_core.equity_owner_readiness_recovery_execution.execution_boundary import build_boundary_check


def test_recovery_execution_boundaries_block_forbidden_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    report_dir = paths.outputs_dir / "equity_owner_readiness_recovery_execution" / "daily" / AS_OF_DATE
    (report_dir / "BAD.md").write_text("买入建议", encoding="utf-8")
    boundary = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE)
    assert boundary["overall_passed"] is False
    assert boundary["forbidden_wording_positive_hits"]


def test_recovery_execution_boundaries_preserve_no_execution_flags(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    boundary = execution_data(paths, "recovery_execution_boundary_check.json")
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["execute_remediation_actions"] is False
    assert boundary["order_preview_generated"] is False
