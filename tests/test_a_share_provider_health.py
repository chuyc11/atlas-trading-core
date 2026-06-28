from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import make_data_refresh_paths
from trading_core.equity_data_refresh.provider_health import build_provider_health_check
from trading_core.equity_data_refresh.provider_registry import build_provider_registry_snapshot


def test_provider_health_local_and_disabled_network(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    registry = build_provider_registry_snapshot()
    health = build_provider_health_check(paths=paths, registry=registry)
    local = next(row for row in health["providers"] if row["provider_id"] == "local_file_provider")
    public = next(row for row in health["providers"] if row["provider_id"] == "eastmoney_public_provider")
    assert local["local_source_available"] is True
    assert public["enabled"] is False
