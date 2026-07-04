from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_report_deduplication_uses_canonical_pointers_without_rewrite(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    dedup = v24_json(paths, "v24_report_deduplication_result")

    assert dedup["report_deduplication_result_generated"] is True
    assert dedup["historical_reports_rewritten"] is False
    assert dedup["safety_report_deleted"] is False
    assert dedup["audit_report_deleted"] is False
    assert dedup["release_report_deleted"] is False
    assert "audit" in dedup["canonical_pointer_registry"]
    assert dedup["report_inventory_count"] > 0
