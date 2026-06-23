from trading_core.evolution.mistake_classifier import MISTAKE_TYPES, classify_mistakes
from trading_core.storage.file_paths import project_paths


def test_mistake_taxonomy_and_output(sample_workspace) -> None:
    scorecard = {
        "items": [
            {
                "signal_id": "S1",
                "strategy_id": "macro",
                "symbol": "510300.SH",
                "status": "wrong",
                "confidence": 0.7,
                "risk_flags": ["already_priced_in"],
                "excess_return": -0.01,
            }
        ]
    }
    rows = classify_mistakes("2026-06-23", scorecard, paths=project_paths(sample_workspace))
    assert len(MISTAKE_TYPES) >= 5
    assert rows[0]["mistake_type"] == "already_priced_in"
