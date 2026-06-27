from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_json
from trading_core.equity_scoring.score_config import SCORE_COLUMNS


def test_score_distribution_contains_deciles_for_all_scores(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    distribution = score_json(paths, "score_distribution")
    assert distribution["percentile_convention"] == "0_to_100"
    assert distribution["confidence_convention"] == "0_to_1"
    for column in SCORE_COLUMNS:
        score_distribution = distribution["scores"][column]
        assert score_distribution["count"] == 3
        assert 0 <= score_distribution["min"] <= score_distribution["max"] <= 100
        assert sum(score_distribution["deciles"].values()) == 3
