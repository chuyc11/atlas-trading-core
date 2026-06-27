from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_json, make_candidate_paths, relaxed_candidate_config


def test_candidate_generator_outputs_counts_and_artifacts(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    result = build_candidate_package(paths, relaxed_candidate_config())

    assert result["candidate_counts"]["long_candidates"] == 2
    assert result["candidate_counts"]["mid_candidates"] == 2
    assert result["candidate_counts"]["short_candidates"] == 2
    assert result["candidate_counts"]["extended_watch_pool"] == 6
    manifest = candidate_json(paths, "candidate_manifest")
    assert manifest["strict_tradable_count"] == 3
    assert manifest["scored_symbols"] == 3
    assert manifest["boundary"]["buy_sell_signals_generated"] is False
