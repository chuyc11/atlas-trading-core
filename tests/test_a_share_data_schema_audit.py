from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import build_foundation, make_a_share_paths
from trading_core.equity_data_quality.schema_audit import audit_a_share_data_schema


def test_a_share_data_schema_audit_passes_foundation(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    build_foundation(paths)
    result = audit_a_share_data_schema(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["checks"]["daily_price_panel"]["symbol_format_valid"] is True


def test_a_share_data_schema_audit_blocks_duplicate_primary_key(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    build_foundation(paths)
    price_path = paths.data_dir / "equity_market" / "daily_price_panel.parquet"
    frame = pd.read_parquet(price_path)
    pd.concat([frame, frame.iloc[[0]]], ignore_index=True).to_parquet(price_path, index=False)
    result = audit_a_share_data_schema(paths=paths)
    assert result["overall_passed"] is False
    assert "daily_price_panel.no_duplicate_primary_keys=false" in result["blocking_reasons"]

