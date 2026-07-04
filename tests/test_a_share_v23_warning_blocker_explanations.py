from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_warning_blocker_explanations_keep_blockers_visible(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    explanations = v23_json(paths, "v23_warning_blocker_explanation_result")

    assert explanations["warning_explanation_registry_generated"] is True
    assert explanations["blocker_explanation_registry_generated"] is True
    assert explanations["blocker_downgraded_to_warning"] is False
    assert explanations["warning_hidden"] is False
    assert explanations["automatic_waiver_applied"] is False
    assert explanations["threshold_lowered"] is False
