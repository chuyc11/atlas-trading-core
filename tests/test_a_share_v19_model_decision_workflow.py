from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_decision_workflow_keeps_watch_research_only(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    decision = v19_json(paths, "v19_model_decision_workflow_result")

    assert result["model_decision_workflow_result_generated"] is True
    assert decision["model_status"] == "watch"
    assert "real_trading_active" not in decision["allowed_statuses"]
    assert decision["model_status_real_trading_active_present"] is False
    assert decision["model_approval_hard_gate"] == "blocked"
    assert decision["model_watch_hard_gate"] == "passed"
    assert decision["model_approval_enters_real_trading"] is False
