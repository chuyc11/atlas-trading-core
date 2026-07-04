from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json
from trading_core.equity_v24_maintenance_quality.builder import JSON_NAMES, MARKDOWN_NAMES


def test_v24_artifact_inventory_bloat_result_and_budget(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    result, audit = build_v24(paths)
    inventory = v24_json(paths, "v24_artifact_inventory_bloat_result")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert inventory["artifact_inventory_bloat_result_generated"] is True
    assert inventory["artifact_inventory_fabricated"] is False
    assert inventory["artifact_count_total"] > 0
    assert "result_json" in inventory["artifact_count_by_type"]
    assert len(JSON_NAMES) <= 28
    assert len(MARKDOWN_NAMES) <= 8
    assert result["required_artifacts_deleted"] is False
    assert result["historical_evidence_deleted"] is False
