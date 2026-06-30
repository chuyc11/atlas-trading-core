from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_readiness_gate.io import load_json, write_json


def seed_owner_readiness_gate_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_daily_pack_history_outputs(paths, as_of_date)
    from trading_core.equity_owner_daily_pack_history.daily_pack_history_audit import audit_a_share_owner_daily_pack_history

    audit_a_share_owner_daily_pack_history(as_of_date=as_of_date, paths=paths)


def seed_owner_readiness_gate_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_owner_readiness_gate_inputs(paths, as_of_date)
    from trading_core.equity_owner_readiness_gate.gate_builder import build_a_share_owner_readiness_gate

    return build_a_share_owner_readiness_gate(as_of_date=as_of_date, paths=paths)


def gate_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date / name)
