from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE


def test_v24_result_and_audit_enforce_safety_boundaries(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    result, audit = build_v24(paths)
    safety = v24_json(paths, "v24_safety_boundary_sweep")
    protected = v24_json(paths, "v24_protected_path_sweep")

    assert audit["overall_passed"] is True
    assert result["overall_passed"] is True
    assert safety["safety_boundary_sweep_passed"] is True
    assert protected["protected_path_sweep_passed"] is True
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["full_pytest_run"] is False
    assert result["targeted_pytest_required"] is True
