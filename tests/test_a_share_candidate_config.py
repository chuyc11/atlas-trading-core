from __future__ import annotations

from trading_core.equity_selection.candidate_config import CANDIDATE_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, CandidateGenerationConfig, validate_candidate_config


def test_candidate_config_defaults_and_boundary() -> None:
    config = CandidateGenerationConfig()
    payload = config.to_dict()

    assert payload["target_version"] == TARGET_VERSION
    assert payload["long_count"] == 30
    assert payload["extended_count"] == 100
    assert payload["boundary"] == CANDIDATE_BOUNDARY
    assert payload["boundary"]["candidates_generated"] is True
    assert payload["boundary"]["virtual_portfolio_generated"] is False
    assert RECOMMENDED_NEXT_VERSION == "v0.7.6-a-share-virtual-portfolio-construction"
    assert validate_candidate_config(config) == []
