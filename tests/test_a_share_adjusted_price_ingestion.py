from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices


def test_a_share_adjusted_price_ingestion_records_raw_fallback(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_adjusted_prices(paths=paths)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 6
    assert result["adjustment_types"] == ["raw"]
    assert result["adjusted_price_status"] == "raw_fallback"
    assert result["true_adjustment_factor_available"] is False
    assert result["raw_price_used_as_adjusted_price_fallback"] is True
    assert frame["adj_factor"].eq(1.0).all()
