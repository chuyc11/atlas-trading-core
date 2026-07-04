from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_test_and_code_maintenance_reports_keep_assertions_intact(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    tests = v24_json(paths, "v24_test_maintenance_result")
    code = v24_json(paths, "v24_code_organization_result")

    assert tests["test_maintenance_result_generated"] is True
    assert tests["test_files_scanned"] > 0
    assert tests["safety_tests_deleted"] is False
    assert tests["assertion_strength_lowered"] is False
    assert tests["failing_tests_skipped"] is False
    assert tests["xfail_added_to_bypass_issue"] is False
    assert code["code_organization_result_generated"] is True
    assert code["scope_controlled"] is True
