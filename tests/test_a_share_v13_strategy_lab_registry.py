from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_strategy_lab_registry_and_cards(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)

    registry = v13_json(paths, "v13_strategy_lab_registry_expansion")
    cards = v13_json(paths, "v13_strategy_card_register")

    assert result["strategy_lab_registry_expanded"] is True
    assert registry["strategy_real_trading_active_state_present"] is False
    assert "quality_blocked" in registry["strategy_states"]
    assert cards["strategy_card_register_generated"] is True
    assert cards["all_cards_simulation_only"] is True
