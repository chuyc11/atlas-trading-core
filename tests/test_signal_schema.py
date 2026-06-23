from trading_core.signals.macro_signal_loader import filter_china_macro_signals
from trading_core.signals.signal_generator import generate_trading_signals
from trading_core.universe.universe_loader import load_universe


def test_macro_signal_generates_trading_signal_and_filters_universe() -> None:
    universe = load_universe()
    macro = [
        {
            "macro_signal_id": "M1",
            "region": "CHINA",
            "confidence": "medium",
            "affected_assets": ["510300.SH", "BAD.SH"],
            "scenario": "test",
            "risk_flags": [],
        }
    ]
    filtered = filter_china_macro_signals(macro, universe)
    signals = generate_trading_signals(filtered, "2026-06-23", universe=universe)
    assert [signal["symbol"] for signal in signals] == ["510300.SH"]
    assert signals[0]["status"] == "candidate"
