from __future__ import annotations

from trading_core.equity_scoring.normalization import VALID_DIRECTIONS
from trading_core.equity_scoring.score_config import SCORE_BOUNDARY, TARGET_VERSION, default_score_config, validate_score_config


def test_score_config_loads_weights_and_boundary() -> None:
    config = default_score_config()

    assert config["score_version"] == TARGET_VERSION
    assert validate_score_config(config) == []
    assert config["normalization_method"] == "cross_sectional_percentile_rank"
    assert config["winsorization_limits"] == {"lower": 0.01, "upper": 0.99}
    assert set(config["feature_directions"].values()).issubset(VALID_DIRECTIONS)
    for weights in config["component_weights"].values():
        assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert config["boundary"] == SCORE_BOUNDARY
    assert config["boundary"]["scores_generated"] is True
    assert config["boundary"]["candidates_generated"] is False
