from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_data_quality.common import write_json
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_owner_monitoring.monitoring_audit import audit_a_share_owner_monitoring
from trading_core.equity_owner_monitoring.monitoring_builder import build_a_share_owner_monitoring
from trading_core.equity_owner_remediation.remediation_audit import audit_a_share_owner_remediation
from trading_core.equity_owner_remediation.remediation_builder import build_a_share_owner_remediation


def seed_remediation_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_monitoring_inputs(paths, as_of_date)
    _seed_required_refresh_remediation_artifacts(paths, as_of_date)
    build_a_share_owner_monitoring(as_of_date=as_of_date, paths=paths)
    audit_a_share_owner_monitoring(as_of_date=as_of_date, paths=paths)


def build_remediation_artifacts(paths, as_of_date: str = AS_OF_DATE):
    seed_remediation_inputs(paths, as_of_date)
    build_result = build_a_share_owner_remediation(as_of_date=as_of_date, paths=paths)
    audit = audit_a_share_owner_remediation(as_of_date=as_of_date, paths=paths)
    return build_result, audit


def _seed_required_refresh_remediation_artifacts(paths, as_of_date: str) -> None:
    artifacts = data_refresh_artifact_paths(paths, as_of_date)
    placeholders = {
        "provider_fallback_report": {"report_id": "TEST-PROVIDER-FALLBACK", "target_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening", "as_of_date": as_of_date},
        "dataset_schema_validation": {"validation_id": "TEST-SCHEMA", "target_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening", "as_of_date": as_of_date, "overall_passed": True},
    }
    for key, payload in placeholders.items():
        if not artifacts[key].exists():
            write_json(artifacts[key], payload)
