from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_outputs
from trading_core.equity_owner_closeout_review.io import load_json


def seed_closeout_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_v0820_outputs(paths, as_of_date)


def seed_closeout_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_closeout_inputs(paths, as_of_date)
    from trading_core.equity_owner_closeout_review.builder import build_a_share_owner_closeout_review

    return build_a_share_owner_closeout_review(as_of_date=as_of_date, paths=paths)


def closeout_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date / name)
