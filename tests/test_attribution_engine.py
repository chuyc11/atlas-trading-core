from trading_core.attribution.attribution_engine import build_attribution
from trading_core.storage.file_paths import project_paths


def test_attribution_json_generates(sample_workspace) -> None:
    portfolio = {
        "account_id": "CHINA_PAPER",
        "total_asset": 100000,
        "daily_return": 0.01,
        "positions": [{"symbol": "510300.SH", "unrealized_pnl": 100, "strategy_id": "macro"}],
    }
    benchmark = {"excess_return": {"CASH": 0.01}}
    attribution = build_attribution("2026-06-23", portfolio, [], benchmark, paths=project_paths(sample_workspace))
    assert attribution["total_pnl"] > 0
    assert attribution["residual_pnl"] == 0
    assert "510300.SH" in attribution["holding_contribution"]
