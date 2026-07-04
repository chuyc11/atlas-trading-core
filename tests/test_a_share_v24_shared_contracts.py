from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_shared_result_and_audit_contract_reviews_are_read_only(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    shared = v24_json(paths, "v24_shared_result_contract_result")
    audit_contract = v24_json(paths, "v24_audit_contract_consolidation_result")

    assert shared["shared_result_contract_result_generated"] is True
    assert audit_contract["audit_contract_consolidation_result_generated"] is True
    assert shared["historical_result_json_rewritten"] is False
    assert shared["historical_fields_deleted"] is False
    assert shared["audit_severity_lowered"] is False
    assert shared["blocker_converted_to_warning"] is False
    assert shared["auto_waiver_applied"] is False
    assert "research_only" in shared["common_safety_fields_registry"]
