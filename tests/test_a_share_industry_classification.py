from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_industry.classification import ingest_a_share_industry_classification


def test_a_share_industry_classification_records_board_fallback(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_industry_classification(paths=paths)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 6
    assert result["industry_standard"] == "board_fallback"
    assert {"STAR", "CHINEXT", "BSE"}.issubset(set(frame["industry_level_2"]))

