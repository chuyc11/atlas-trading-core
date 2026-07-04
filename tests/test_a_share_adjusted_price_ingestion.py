from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices, validate_adjusted_price_status


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


def test_adjusted_price_validator_rejects_raw_fallback_unless_explicitly_allowed(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_adjusted_prices(paths=paths)

    blocked = validate_adjusted_price_status(paths=paths)
    allowed = validate_adjusted_price_status(paths=paths, allow_raw_price=True)

    assert result["adjusted_price_status"] == "raw_fallback"
    assert blocked["passed"] is False
    assert blocked["adjusted_price_status"] == "raw_fallback"
    assert allowed["passed"] is True
    assert allowed["degraded"] is True
