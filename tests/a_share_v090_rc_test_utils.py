from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_outputs
from trading_core.equity_owner_v090_rc.io import load_json


def seed_v090_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_closeout_outputs(paths, as_of_date)


def seed_v090_outputs(paths, as_of_date: str = AS_OF_DATE, *, skip_full_pytest: bool = True):
    seed_v090_inputs(paths, as_of_date)
    from trading_core.equity_owner_v090_rc.builder import build_a_share_owner_v090_rc

    return build_a_share_owner_v090_rc(as_of_date=as_of_date, paths=paths, skip_full_pytest=skip_full_pytest)


def v090_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date / name)
