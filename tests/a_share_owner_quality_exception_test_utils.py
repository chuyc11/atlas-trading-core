from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths as make_paths
from tests.a_share_owner_readiness_gate_test_utils import seed_owner_readiness_gate_inputs
from trading_core.equity_owner_quality_exceptions.io import load_json


def seed_owner_quality_exception_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_readiness_gate_inputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_gate.gate_builder import build_a_share_owner_readiness_gate
    from trading_core.equity_owner_readiness_gate.owner_readiness_gate_audit import audit_a_share_owner_readiness_gate

    build_a_share_owner_readiness_gate(as_of_date=as_of_date, paths=paths, minimum_owner_readiness_score=100)
    audit_a_share_owner_readiness_gate(as_of_date=as_of_date, paths=paths)


def seed_owner_quality_exception_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_owner_quality_exception_inputs(paths, as_of_date)
    from trading_core.equity_owner_quality_exceptions.quality_exception_builder import build_a_share_owner_quality_exceptions

    return build_a_share_owner_quality_exceptions(as_of_date=as_of_date, paths=paths)


def exception_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date / name)
