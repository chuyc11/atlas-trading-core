from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, seed_recovery_execution_outputs
from trading_core.equity_owner_controlled_gate_reevaluation.io import load_json


def seed_controlled_gate_reevaluation_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_recovery_execution_outputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_recovery_execution.recovery_execution_audit import audit_a_share_owner_readiness_recovery_execution

    audit_a_share_owner_readiness_recovery_execution(as_of_date=as_of_date, paths=paths)


def seed_controlled_gate_reevaluation_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_controlled_gate_reevaluation_inputs(paths, as_of_date)
    from trading_core.equity_owner_controlled_gate_reevaluation.controlled_builder import build_a_share_owner_controlled_gate_reevaluation

    return build_a_share_owner_controlled_gate_reevaluation(as_of_date=as_of_date, paths=paths)


def controlled_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date / name)

