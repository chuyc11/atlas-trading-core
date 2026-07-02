from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_model_registry_and_cards_do_not_include_real_trading_active(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    registry = v18_json(paths, "v18_model_registry")
    cards = v18_json(paths, "v18_model_card_register")

    assert result["model_registry_generated"] is True
    assert registry["model_status"] == "watch"
    assert "real_trading_active" not in registry["allowed_statuses"]
    assert registry["model_status_real_trading_active_present"] is False
    assert cards["model_card_schema_generated"] is True
    assert cards["model_card_displays_simulation_only"] is True
    assert cards["model_status_real_trading_active_present"] is False
