from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_public_data_source_adapter_registry_has_no_private_adapters(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    registry = v21_json(paths, "v21_public_data_source_adapter_registry")

    assert result["v20_baseline_verified"] is True
    assert registry["public_data_source_adapter_registry_generated"] is True
    assert result["broker_adapter_added"] is False
    assert result["private_account_adapter_added"] is False
    assert result["fabricated_data_source"] is False
    assert {adapter["source_type"] for adapter in registry["adapters"]} <= {"local_file", "public_index_data", "public_market_data"}
