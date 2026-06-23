from trading_core.evolution.signal_scorecard import score_signals
from trading_core.storage.file_paths import project_paths


def test_signal_scorecard_validates_outperformance(sample_workspace) -> None:
    scorecard = score_signals(
        "2026-06-23",
        [{"signal_id": "S1", "strategy_id": "macro", "symbol": "510300.SH", "side": "LONG"}],
        [{"signal_id": "S1"}],
        {"daily_return": 0.02},
        {"benchmarks": {"EQUAL_ETF": {"return": 0.01}}},
        paths=project_paths(sample_workspace),
    )
    assert scorecard["items"][0]["status"] == "validated"
