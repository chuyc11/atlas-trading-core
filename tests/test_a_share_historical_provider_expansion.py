from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import make_history_paths
from trading_core.integrations.public_data.historical_provider_registry import select_history_symbols


def test_select_history_symbols_defaults_to_full_equity_master(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)

    symbols = select_history_symbols(paths)

    assert len(symbols) == 6
    assert "600000.SH" in symbols
    assert "000001.SZ" in symbols


def test_select_history_symbols_explicit_limit_only(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)

    assert len(select_history_symbols(paths, max_symbols=0)) == 6
    assert len(select_history_symbols(paths, max_symbols=2)) == 2
