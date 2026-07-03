from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_release_lineage_registry_and_result(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)

    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    lineage = v20_json(paths, "v20_release_lineage_registry")

    assert result["overall_passed"] is True
    assert result["v19_baseline_verified"] is True
    assert lineage["release_lineage_registry_generated"] is True
    assert len(lineage["lineage_entries"]) >= 13
    assert lineage["lineage_entries"][-1]["version"] == "v1.9.0"
    assert lineage["v19_baseline_verified"] is True
