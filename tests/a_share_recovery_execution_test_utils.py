from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_recovery_outputs
from trading_core.equity_owner_readiness_recovery_execution.io import load_json


def seed_recovery_execution_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_readiness_recovery_outputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_recovery.recovery_audit import audit_a_share_owner_readiness_recovery

    audit_a_share_owner_readiness_recovery(as_of_date=as_of_date, paths=paths)


def seed_recovery_execution_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_recovery_execution_inputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_recovery_execution.execution_builder import build_a_share_owner_readiness_recovery_execution

    return build_a_share_owner_readiness_recovery_execution(as_of_date=as_of_date, paths=paths)


def execution_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date / name)
