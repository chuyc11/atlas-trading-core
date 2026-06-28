from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import audit_attribution_package, build_attribution_package, make_attribution_paths


def test_attribution_audit_pass(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    audit = audit_attribution_package(paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["risk_checks"]["risk_downgraded_symbols_in_portfolio"] == []
