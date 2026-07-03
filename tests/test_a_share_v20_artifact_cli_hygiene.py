from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v20_platform_closeout


def test_v20_artifact_cli_repository_hygiene(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    hygiene = v20_json(paths, "v20_artifact_cli_repository_hygiene_result")
    manifest = v20_json(paths, "v20_platform_closeout_manifest")

    assert result["artifact_cli_repository_hygiene_generated"] is True
    assert hygiene["artifact_budget_review"]["json_count"] == len(JSON_NAMES)
    assert hygiene["artifact_budget_review"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert "build-a-share-v20-platform-closeout" in hygiene["cli_surface_inventory"]
    assert hygiene["old_run_daily_absent"] is True
    assert manifest["json_artifact_count"] == len(JSON_NAMES)
