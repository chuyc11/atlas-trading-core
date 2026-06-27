from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_data_dir, make_candidate_paths, relaxed_candidate_config
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_selection.candidate_generation_audit import audit_a_share_candidates


def test_candidate_generation_audit_passes_and_fails_closed_for_missing_manifest(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config())

    audit = audit_a_share_candidates(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["counts"]["long_candidates"] == 2

    (candidate_data_dir(paths) / "candidate_manifest.json").unlink()
    failed = audit_a_share_candidates(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert failed["overall_passed"] is False
    assert "candidate_manifest_exists=false" in failed["blocking_reasons"]
