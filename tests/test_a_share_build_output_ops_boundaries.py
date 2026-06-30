from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_no_forbidden_boundaries_or_protected_paths(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    boundary = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_boundary_check.json")
    assert boundary["forbidden_artifacts_present"] == []
    assert boundary["forbidden_wording_positive_hits"] == []
    for protected in [
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]:
        assert not protected.exists()

