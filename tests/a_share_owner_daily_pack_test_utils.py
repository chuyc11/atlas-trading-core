from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from tests.a_share_owner_dashboard_test_utils import write_json


def seed_owner_daily_pack_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_build_output_ops_outputs(paths, as_of_date)
    from trading_core.equity_build_output_ops_refresh.build_output_ops_audit import (
        audit_a_share_build_output_ops_refresh,
    )

    audit_a_share_build_output_ops_refresh(as_of_date=as_of_date, paths=paths)


def seed_owner_daily_pack_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_owner_daily_pack_inputs(paths, as_of_date)
    from trading_core.equity_owner_daily_pack.daily_pack_builder import build_a_share_owner_daily_pack

    return build_a_share_owner_daily_pack(as_of_date=as_of_date, paths=paths)
