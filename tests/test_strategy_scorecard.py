from trading_core.evolution.strategy_scorecard import score_strategies
from trading_core.storage.file_paths import project_paths


def test_strategy_scorecard_outputs_recommendation(sample_workspace) -> None:
    scorecard = {
        "items": [
            {"signal_id": "S1", "strategy_id": "macro", "status": "wrong", "excess_return": -0.01}
        ]
    }
    payload = score_strategies("2026-06-23", scorecard, [], paths=project_paths(sample_workspace))
    assert payload["items"][0]["status_recommendation"] == "pause_or_shadow"
