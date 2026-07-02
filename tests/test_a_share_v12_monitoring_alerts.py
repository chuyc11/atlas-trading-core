from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import ALERT_IDS, run_a_share_v12_continuous_ops


def test_v12_monitoring_alerts_expansion_is_local_internal(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    alerts = v12_json(paths, "v12_monitoring_alerts_result")

    assert result["monitoring_alerts_generated"] is True
    assert {row["alert_id"] for row in alerts["alerts"]} == set(ALERT_IDS)
    assert all(row["local_internal_only"] for row in alerts["alerts"])
    assert alerts["external_notifications_sent"] is False
    assert any(row["alert_id"] == "BENCHMARK-MISSING" and row["active"] for row in alerts["alerts"])
    assert any(row["alert_id"] == "CLAIM-GUARD-BLOCKED" and row["active"] for row in alerts["alerts"])
