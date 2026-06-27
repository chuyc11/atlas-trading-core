from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, portfolio_data_dir, portfolio_frame, relaxed_portfolio_config
from trading_core.equity_portfolios.virtual_portfolio_audit import audit_a_share_virtual_portfolios


def test_virtual_portfolio_audit_passes_and_fails_closed_for_missing_manifest(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())

    audit = audit_a_share_virtual_portfolios(paths=paths, as_of_date=AS_OF_DATE)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["counts"]["long_holdings"] == 2

    (portfolio_data_dir(paths) / "portfolio_manifest.json").unlink()
    failed = audit_a_share_virtual_portfolios(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "portfolio_manifest_exists=false" in failed["blocking_reasons"]


def test_virtual_portfolio_audit_blocks_risk_downgraded_inclusion(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    symbol = str(portfolio_frame(paths, "long_virtual_portfolio_parquet").iloc[0]["symbol"])
    risk_path = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "risk_downgraded_candidates.json"
    risk_path.write_text(json.dumps([{"symbol": symbol}], ensure_ascii=False), encoding="utf-8")

    failed = audit_a_share_virtual_portfolios(paths=paths, as_of_date=AS_OF_DATE)

    assert failed["overall_passed"] is False
    assert "no_risk_downgraded_symbols_in_main_portfolios=false" in failed["blocking_reasons"]

