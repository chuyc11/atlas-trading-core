from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_artifact_index_health_and_platform_health(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    index = v12_json(paths, "v12_artifact_index_result")
    health = v12_json(paths, "v12_artifact_health_result")
    platform = v12_json(paths, "v12_platform_health_result")
    protected = v12_json(paths, "v12_protected_path_sweep")

    assert result["artifact_index_generated"] is True
    assert index["daily_artifact_manifest_index_generated"] is True
    assert index["latest_pointer"].endswith("2026-07-01")
    assert health["artifact_health_passed"] is True
    assert health["required_artifact_presence_check"] is True
    assert platform["platform_health_report_generated"] is True
    assert protected["protected_path_sweep_passed"] is True
