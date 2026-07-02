from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_monitoring_alerts_and_remediation_are_local_internal(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    monitoring = v11_json(paths, "v11_monitoring_alerts_result")
    remediation = v11_json(paths, "v11_remediation_checklist_result")

    assert result["monitoring_alerts_generated"] is True
    assert result["remediation_checklist_generated"] is True
    assert {"DATA-STALE", "BENCHMARK-MISSING", "CLAIM-GUARD-BLOCKED", "PAPER-LEDGER-MISMATCH", "SIMULATED-EXECUTION-ANOMALY", "STRATEGY-PROMOTION-BLOCKED", "FORBIDDEN-WORDING", "PROTECTED-PATH-MODIFICATION"} == {row["alert_id"] for row in monitoring["alerts"]}
    assert monitoring["external_notifications_sent"] is False
    assert remediation["checklist"]
