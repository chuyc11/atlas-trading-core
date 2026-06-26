from __future__ import annotations

from pathlib import Path

import pytest

from a_share_data_test_utils import make_a_share_paths


def test_a_share_data_foundation_cli_smoke_and_no_trading_side_effects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_a_share_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    commands = [
        "equity-data-source-manifest",
        "build-a-share-equity-master",
        "build-a-share-trading-calendar",
        "ingest-a-share-daily-prices",
        "ingest-a-share-adjusted-prices",
        "ingest-a-share-daily-basic",
        "ingest-a-share-industry-classification",
        "ingest-a-share-basic-financials",
        "audit-a-share-data-coverage",
        "audit-a-share-data-schema",
        "build-a-share-data-foundation",
    ]
    for command in commands:
        assert cli.main([command]) == 0
    assert not (paths.data_dir / "forward_dry_run" / "day_002").exists()
    assert not (paths.data_dir / "orders").exists()
    assert not (paths.data_dir / "trades").exists()
    assert not (paths.data_dir / "equity_scores").exists()
    assert not (paths.data_dir / "equity_selection").exists()
    assert not (paths.data_dir / "equity_portfolios").exists()
