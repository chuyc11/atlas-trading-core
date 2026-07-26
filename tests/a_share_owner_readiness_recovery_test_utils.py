from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, make_paths as make_paths, seed_owner_quality_exception_outputs
from trading_core.equity_owner_readiness_recovery.io import load_json


def seed_owner_readiness_recovery_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_quality_exception_outputs(paths, as_of_date)
    from trading_core.equity_owner_quality_exceptions.quality_exception_audit import audit_a_share_owner_quality_exceptions

    audit_a_share_owner_quality_exceptions(as_of_date=as_of_date, paths=paths)


def seed_owner_readiness_recovery_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_owner_readiness_recovery_inputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_recovery.recovery_builder import build_a_share_owner_readiness_recovery

    return build_a_share_owner_readiness_recovery(as_of_date=as_of_date, paths=paths)


def recovery_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date / name)
