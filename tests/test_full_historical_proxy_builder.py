from __future__ import annotations

import json
from pathlib import Path

from global_briefing_test_utils import make_paths
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals


def test_full_historical_proxy_output_passes_signal_contract(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    result = normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    validation = validate_global_briefing_signals(result["proxy_package"]["normalized_path"], start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert validation["overall_passed"] is True
    assert Path(result["proxy_package"]["package_path"]).exists()


def test_full_historical_proxy_uses_epu_and_oecd_components(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    result = normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    rows = [json.loads(line) for line in Path(result["proxy_package"]["normalized_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    assert any(row["signals"].get("policy_uncertainty") is not None for row in rows)
    assert any(row["signals"].get("macro_cycle_pressure") is not None for row in rows)
    assert "epu" in result["proxy_package"]
    assert "oecd" in result["proxy_package"]
