from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.ops_digest import build_monitoring_remediation_ops_digest


def test_monitoring_remediation_ops_digest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_monitoring_remediation_ops_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["digest_id"] == "A-SHARE-MONITORING-REMEDIATION-OPS-DIGEST"
    assert digest["execute_remediation_actions"] is False
    assert digest["external_notifications_sent"] is False
