from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_industry_sector_sources_keep_pit_warning_and_no_fabrication(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    industry = v21_json(paths, "v21_industry_sector_source_result")

    assert result["industry_sector_source_result_generated"] is True
    assert industry["industry_sector_source_result_generated"] is True
    assert industry["fabricated_industry_classification"] is False
    assert industry["classification_backfilled_silently"] is False
    assert industry["future_industry_membership_used"] is False
    assert industry["pit_warning_when_missing"] is True
