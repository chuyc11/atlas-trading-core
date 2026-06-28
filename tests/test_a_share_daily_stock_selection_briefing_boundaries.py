from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import build_briefing_package, make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_briefings.briefing_audit import audit_a_share_daily_stock_selection_briefing


def test_briefing_boundaries_and_forbidden_artifacts(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)
    audit = audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)

    assert audit["boundary"]["briefing_only"] is True
    assert audit["boundary"]["scores_regenerated"] is False
    assert audit["boundary"]["candidates_regenerated"] is False
    assert audit["boundary"]["virtual_portfolios_regenerated"] is False
    assert audit["boundary"]["buy_sell_signals_generated"] is False
    assert audit["boundary"]["order_preview_generated"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["boundary"]["real_orders_placed"] is False
    assert audit["boundary"]["model_profit_guaranteed"] is False
    assert audit["boundary"]["live_trading_ready"] is False
    assert audit["forbidden_artifacts"]["buy_sell_signal_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["order_preview_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["broker_order_artifacts_present"] == []
    assert audit["forbidden_artifacts"]["real_order_artifacts_present"] == []
