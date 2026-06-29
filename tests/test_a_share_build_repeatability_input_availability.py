from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths
from tests.a_share_gated_build_test_utils import seed_gated_build_outputs
from trading_core.equity_build_repeatability.input_availability import build_repeatability_input_availability


def test_repeatability_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_outputs(paths)
    result = build_repeatability_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["gated_build_audit_passed"] is True


def test_repeatability_input_availability_fails_missing(tmp_path):
    paths = make_paths(tmp_path)
    result = build_repeatability_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
    assert any(reason.startswith("missing_required_input") for reason in result["blocking_reasons"])

