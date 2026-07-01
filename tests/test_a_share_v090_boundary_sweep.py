from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_owner_v090_rc.boundary_sweep import build_boundary_sweep_result


def test_v090_boundary_sweep_detects_forbidden_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    clean = build_boundary_sweep_result(paths=paths, as_of_date=AS_OF_DATE)
    assert clean["boundary_sweep_passed"] is True
    bad = paths.data_dir / "equity_owner_v090_rc" / "daily" / AS_OF_DATE / "BROKER_ORDER.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{}", encoding="utf-8")
    failed = build_boundary_sweep_result(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["boundary_sweep_passed"] is False
    assert "forbidden_artifacts_present" in failed["blocking_reasons"]
