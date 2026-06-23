from trading_core.universe.universe_loader import load_universe, universe_symbols
from trading_core.universe.universe_versioning import stable_universe_id, stamp_record_with_universe


def test_universe_loads_and_filters() -> None:
    universe = load_universe()
    assert "510300.SH" in universe_symbols(universe, market="A_SHARE")
    assert stable_universe_id(universe) == "china_etf_core_v1"
    assert stamp_record_with_universe({"x": 1}, universe)["universe_id"] == "china_etf_core_v1"
