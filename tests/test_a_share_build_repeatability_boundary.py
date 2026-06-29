from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_repeatability.repeatability_boundary import build_repeatability_boundary_check


def test_repeatability_boundary_stays_clean(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_repeatability_boundary_check(
        paths=paths,
        as_of_date=AS_OF_DATE,
        execution_record={"command_executed": True, "workflow_audit_overall_passed": True, "blocking_reasons": [], "warnings": []},
        protected_check={"protected_path_modifications_detected": False, "blocking_reasons": [], "warnings": []},
        comparison={"comparison_completed": True, "blocking_reasons": []},
        drift_summary={"blocking_reasons": []},
    )
    assert boundary["overall_passed"] is True
    assert boundary["build_repeatability_used_as_trade_instruction"] is False

