from __future__ import annotations

from trading_core.evolution.promotion_evidence import evaluate_verified_shadow_promotion
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import write_json
import pytest

pytestmark = pytest.mark.smoke


def test_first_day_without_verified_shadow_evidence_never_promotes(tmp_path) -> None:
    result = evaluate_verified_shadow_promotion("momentum_shadow_v1", "2026-07-10", project_paths(tmp_path))

    assert result["recommended_state"] == "shadow"
    assert result["auto_applied"] is False
    assert result["evidence_status"] == "insufficient"


def test_verified_out_of_sample_evidence_can_only_recommend_small_activation(tmp_path) -> None:
    paths = project_paths(tmp_path)
    evidence = paths.data_dir / "experiments" / "shadow_evaluation-momentum_shadow_v1-2026-07-10.json"
    write_json(
        evidence,
        {
            "evidence_kind": "out_of_sample_shadow",
            "strategy_id": "momentum_shadow_v1",
            "as_of_date": "2026-07-10",
            "unique_days": 20,
            "signal_count": 12,
            "net_excess_return": 0.02,
            "mistake_rate": 0.1,
            "max_drawdown": 0.02,
            "future_data_flag": False,
            "benchmark_comparison": True,
            "costs_included": True,
            "source_hashes": ["abc"],
        },
    )

    result = evaluate_verified_shadow_promotion("momentum_shadow_v1", "2026-07-10", paths)

    assert result["recommendation"] == "promote_to_active_small"
    assert result["recommended_state"] == "active_small"
    assert result["auto_applied"] is False


def test_malformed_evidence_fails_closed_instead_of_raising(tmp_path) -> None:
    paths = project_paths(tmp_path)
    evidence = paths.data_dir / "experiments" / "shadow_evaluation-momentum_shadow_v1-2026-07-10.json"
    write_json(
        evidence,
        {
            "evidence_kind": "out_of_sample_shadow",
            "strategy_id": "momentum_shadow_v1",
            "as_of_date": "2026-07-10",
            "unique_days": "not-a-number",
            "signal_count": 12,
            "net_excess_return": None,
            "mistake_rate": 2,
            "max_drawdown": "nan",
            "future_data_flag": False,
            "benchmark_comparison": True,
            "costs_included": True,
            "source_hashes": [],
        },
    )

    result = evaluate_verified_shadow_promotion("momentum_shadow_v1", "2026-07-10", paths)

    assert result["recommended_state"] == "shadow"
    assert result["auto_applied"] is False
    assert result["evidence_status"] == "insufficient"
    assert "invalid_unique_days" in result["failed_evidence_rules"]
    assert "invalid_net_excess_return" in result["failed_evidence_rules"]
    assert "mistake_rate_out_of_range" in result["failed_evidence_rules"]
    assert "invalid_max_drawdown" in result["failed_evidence_rules"]
