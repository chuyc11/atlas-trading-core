from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, relaxed_portfolio_config
from trading_core.equity_portfolios.virtual_portfolio_audit import audit_a_share_virtual_portfolios


def test_virtual_portfolio_boundaries_and_forbidden_artifacts(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    audit = audit_a_share_virtual_portfolios(paths=paths, as_of_date=AS_OF_DATE)

    assert audit["boundary"]["virtual_portfolio_generated"] is True
    assert audit["boundary"]["real_portfolio_generated"] is False
    assert audit["boundary"]["buy_sell_signals_generated"] is False
    assert audit["boundary"]["order_preview_generated"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["boundary"]["real_orders_placed"] is False
    assert audit["boundary"]["model_profit_guaranteed"] is False
    assert audit["forbidden_artifacts"]["buy_sell_signal_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["order_preview_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["broker_order_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["real_order_artifacts_present"] == []
    assert audit["intersections"]["excluded_universe_symbols_included"] == []

