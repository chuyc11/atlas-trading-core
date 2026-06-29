from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_remediation_test_utils import build_remediation_artifacts
from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import write_json
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_ops_center.ops_audit import audit_a_share_daily_ops_center
from trading_core.equity_ops_center.ops_builder import build_a_share_daily_ops_center


def seed_ops_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    build_remediation_artifacts(paths, as_of_date)
    _seed_required_ops_input_artifacts(paths, as_of_date)


def build_ops_artifacts(paths, as_of_date: str = AS_OF_DATE):
    seed_ops_inputs(paths, as_of_date)
    build_result = build_a_share_daily_ops_center(as_of_date=as_of_date, paths=paths)
    audit = audit_a_share_daily_ops_center(as_of_date=as_of_date, paths=paths)
    return build_result, audit


def _seed_required_ops_input_artifacts(paths, as_of_date: str) -> None:
    refresh = data_refresh_artifact_paths(paths, as_of_date)
    current = current_day_artifact_paths(paths, as_of_date)
    if not refresh["data_refresh_boundary_check"].exists():
        write_json(
            refresh["data_refresh_boundary_check"],
            {
                "boundary_id": "TEST-DATA-REFRESH-BOUNDARY",
                "target_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening",
                "as_of_date": as_of_date,
                "overall_passed": True,
                "blocking_reasons": [],
                "warnings": [],
            },
        )
    if not current["current_day_readiness"].exists():
        write_json(
            current["current_day_readiness"],
            {
                "readiness_id": "TEST-CURRENT-DAY-READINESS",
                "target_version": "v0.8.1-a-share-current-day-research-workflow-runner",
                "as_of_date": as_of_date,
                "resolved_as_of_date": as_of_date,
                "overall_passed": True,
                "blocking_reasons": [],
                "warnings": [],
            },
        )
