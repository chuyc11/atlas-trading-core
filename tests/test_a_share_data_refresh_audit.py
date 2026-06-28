from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import audit_data_refresh_package, build_data_refresh_package, make_data_refresh_paths


def test_data_refresh_audit_pass_and_fail(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    audit = audit_data_refresh_package(paths)
    assert audit["overall_passed"] is True
    boundary = paths.data_dir / "equity_data_refresh" / "daily" / "2026-06-26" / "data_refresh_boundary_check.json"
    boundary.write_text(boundary.read_text(encoding="utf-8").replace('"broker_connected": false', '"broker_connected": true'), encoding="utf-8")
    failed = audit_data_refresh_package(paths)
    assert failed["overall_passed"] is False
