from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_universe.master import build_a_share_equity_master


def test_a_share_equity_master_schema_and_symbol_normalization(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = build_a_share_equity_master(paths=paths)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbols"] == 6
    assert {"600000.SH", "000001.SZ", "430047.BJ"}.issubset(set(frame["symbol"]))
    assert {"SSE", "SZSE", "BSE"}.issubset(set(frame["exchange"]))
    assert bool(frame.loc[frame["symbol"] == "688001.SH", "is_star_market"].iloc[0]) is True
    assert bool(frame.loc[frame["symbol"] == "300750.SZ", "is_chinext"].iloc[0]) is True
    assert frame["source"].eq("local_file_provider").all()
