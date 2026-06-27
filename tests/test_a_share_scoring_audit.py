from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE, EXCLUDED_SYMBOL
from a_share_score_test_utils import build_score_package, make_score_paths, score_data_dir
from trading_core.equity_scoring.scoring_audit import audit_a_share_scores
from trading_core.equity_scoring.score_config import RECOMMENDED_NEXT_VERSION


def test_scoring_audit_passes_and_fails_closed_for_missing_manifest(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    audit = audit_a_share_scores(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["counts"]["strict_tradable_count"] == 3
    assert audit["counts"]["scored_symbols"] == 3
    assert EXCLUDED_SYMBOL not in audit["score_symbols"] if "score_symbols" in audit else True
    assert audit["recommended_next_version"] == RECOMMENDED_NEXT_VERSION

    (score_data_dir(paths) / "score_manifest.json").unlink()
    failed = audit_a_share_scores(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert failed["overall_passed"] is False
    assert "score_manifest_exists=false" in failed["blocking_reasons"]
