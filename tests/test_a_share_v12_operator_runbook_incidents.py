from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_operator_runbook_incidents_and_retry_recovery(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    runbook = v12_json(paths, "v12_operator_runbook_result")
    incidents = v12_json(paths, "v12_incident_register")
    retry = v12_json(paths, "v12_retry_recovery_plan")

    assert result["operator_runbook_generated"] is True
    assert runbook["pre_run_checklist"]
    assert runbook["post_run_checklist"]
    assert runbook["manual_scheduler_setup_instructions"]
    assert incidents["incident_register_generated"] is True
    assert incidents["incident_severity_classification_generated"] is True
    assert retry["retry_recovery_plan_generated"] is True
    assert retry["automatic_waiver_allowed"] is False
