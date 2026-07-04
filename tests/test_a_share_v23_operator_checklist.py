from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_operator_checklist_is_local_and_cannot_trigger_real_action(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    checklist = v23_json(paths, "v23_operator_checklist_result")

    assert result["operator_checklist_generated"] is True
    assert checklist["local_internal_only"] is True
    assert checklist["operator_checklist_triggers_real_action"] is False
    assert checklist["automatic_operation_triggered"] is False
    assert "what_not_to_do" in checklist["checklists"]
