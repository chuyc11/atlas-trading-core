from __future__ import annotations

import json
from pathlib import Path

from a_share_data_test_utils import build_foundation, make_a_share_paths
from trading_core.equity_data_quality.coverage_audit import audit_a_share_data_coverage


def test_a_share_data_coverage_audit_passes_foundation_and_boundaries(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    build_foundation(paths)
    result = audit_a_share_data_coverage(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["coverage"]["equity_master_symbols"] == 6
    assert result["coverage"]["daily_price_symbols"] == 6
    assert result["boundary"]["scores_generated"] is False
    assert result["boundary"]["selection_generated"] is False
    assert result["boundary"]["virtual_portfolio_generated"] is False
    assert result["boundary"]["day2_executed"] is False
    assert result["boundary"]["run_daily_called"] is False


def test_a_share_data_coverage_audit_fails_when_source_raw_total_is_undercovered(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    build_foundation(paths)
    manifest_path = paths.data_dir / "equity_data_quality" / "a_share_data_source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["rows_available"] = 6
    manifest["raw_total"] = 100
    manifest["raw_coverage_ratio"] = 0.06
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    result = audit_a_share_data_coverage(paths=paths)
    assert result["overall_passed"] is False
    assert result["checks"]["source_rows_cover_raw_total"] is False
    assert "source_rows_cover_raw_total=false" in result["blocking_reasons"]
