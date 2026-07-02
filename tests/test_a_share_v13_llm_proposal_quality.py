from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_llm_proposal_quality_review_is_research_only(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    llm = v13_json(paths, "v13_llm_proposal_quality_result")

    assert result["llm_proposal_quality_result_generated"] is True
    assert result["llm_proposals_are_trade_instructions"] is False
    assert llm["llm_proposals_are_research_drafts_only"] is True
    assert llm["proposal_can_modify_simulated_active_directly"] is False
    assert llm["external_llm_api_called"] is False
