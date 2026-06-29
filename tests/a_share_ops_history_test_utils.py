from tests.a_share_ops_center_test_utils import AS_OF_DATE, build_ops_artifacts
from trading_core.equity_ops_history.ops_history_audit import audit_a_share_ops_history_baseline
from trading_core.equity_ops_history.ops_history_builder import build_a_share_ops_history_baseline


def build_ops_history_artifacts(paths, as_of_date: str = AS_OF_DATE):
    build_ops_artifacts(paths, as_of_date)
    build_result = build_a_share_ops_history_baseline(as_of_date=as_of_date, paths=paths)
    audit = audit_a_share_ops_history_baseline(as_of_date=as_of_date, paths=paths)
    return build_result, audit

