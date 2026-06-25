from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.production_package_acceptance import build_global_briefing_production_acceptance_criteria


def test_acceptance_criteria_json_generated(tmp_path: Path) -> None:
    result = build_global_briefing_production_acceptance_criteria(paths=make_paths(tmp_path))

    assert Path(result["json_path"]).exists()


def test_acceptance_criteria_markdown_and_docs_generated(tmp_path: Path) -> None:
    result = build_global_briefing_production_acceptance_criteria(paths=make_paths(tmp_path))

    assert Path(result["report_path"]).exists()
    assert Path(result["docs_path"]).exists()


def test_acceptance_thresholds_and_zero_leakage(tmp_path: Path) -> None:
    result = build_global_briefing_production_acceptance_criteria(paths=make_paths(tmp_path))

    assert result["required"]["min_coverage"] >= 0.8
    assert result["required"]["target_coverage"] >= 0.9
    assert result["required"]["future_signal_leakage_rows"] == 0


def test_acceptance_non_claims(tmp_path: Path) -> None:
    result = build_global_briefing_production_acceptance_criteria(paths=make_paths(tmp_path))

    for item in ["strategy_effectiveness_proven", "forward_dry_run_validated", "live_trading_ready"]:
        assert item in result["must_not_claim"]


def test_acceptance_criteria_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = build_global_briefing_production_acceptance_criteria(paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_acceptance_criteria_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-production-acceptance-criteria"]) == 0
