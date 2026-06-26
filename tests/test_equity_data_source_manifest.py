from __future__ import annotations

from pathlib import Path

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_data_quality.source_manifest import build_a_share_data_source_manifest


def test_equity_data_source_manifest_records_provider_and_boundaries(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = build_a_share_data_source_manifest(paths=paths)
    assert result["manifest_id"] == "A-SHARE-DATA-SOURCE-MANIFEST"
    assert result["rows_available"] == 6
    assert result["providers_succeeded"] == ["local_file_provider"]
    assert result["external_api_called"] is False
    assert result["real_time_market_data_downloaded"] is False
    assert result["third_party_code_merged_into_main_flow"] is False
    assert result["broker_connected"] is False
    assert result["real_orders_placed"] is False

