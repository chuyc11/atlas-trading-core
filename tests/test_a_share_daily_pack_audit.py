from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.daily_pack_audit import audit_a_share_owner_daily_pack


def test_daily_pack_audit_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)

    audit = audit_a_share_owner_daily_pack(as_of_date=AS_OF_DATE, paths=paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []


def test_daily_pack_audit_fails_when_required_artifact_missing(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    (paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "daily_pack_summary.json").unlink()

    audit = audit_a_share_owner_daily_pack(as_of_date=AS_OF_DATE, paths=paths)

    assert audit["overall_passed"] is False
    assert "json_artifacts_present" in audit["blocking_reasons"]
