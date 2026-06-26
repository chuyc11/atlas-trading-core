from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_fundamental.basic_financials import ingest_a_share_basic_financials


def test_a_share_basic_financials_allows_explicit_partial_fields(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_basic_financials(paths=paths)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 6
    assert result["report_date_coverage"] == 1
    assert all(value == 0.0 for value in result["field_coverage"].values())
    assert frame["source"].eq("local_file_provider").all()

