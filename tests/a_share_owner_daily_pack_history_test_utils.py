from tests.a_share_build_output_ops_test_utils import AS_OF_DATE
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs


def seed_owner_daily_pack_history_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_daily_pack_outputs(paths, as_of_date)
    from trading_core.equity_owner_daily_pack.daily_pack_audit import audit_a_share_owner_daily_pack

    audit_a_share_owner_daily_pack(as_of_date=as_of_date, paths=paths)


def seed_owner_daily_pack_history_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_owner_daily_pack_history_inputs(paths, as_of_date)
    from trading_core.equity_owner_daily_pack_history.daily_pack_history_builder import build_a_share_owner_daily_pack_history

    return build_a_share_owner_daily_pack_history(as_of_date=as_of_date, paths=paths)
