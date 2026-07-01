from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_data_freshness import refresh_a_share_data_freshness, resolve_actual_data_date
from trading_core.storage.file_paths import ProjectPaths


TARGET_DATE = "2026-07-01"


def test_data_freshness_refresh_generates_required_artifacts(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    assert result["overall_passed"] is True
    root = paths.data_dir / "equity_data_freshness" / "daily" / TARGET_DATE
    for name in [
        "data_freshness_refresh_request.json",
        "data_freshness_provider_status.json",
        "data_freshness_coverage_summary.json",
        "data_freshness_refresh_result.json",
        "data_freshness_boundary_check.json",
        "data_freshness_manifest.json",
    ]:
        assert (root / name).exists()
    assert (paths.outputs_dir / "equity_data_freshness" / "daily" / TARGET_DATE / "A_SHARE_DATA_FRESHNESS_REFRESH_RESULT.md").exists()


def test_data_freshness_refresh_request_schema(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, dry_run=True, provider_fetcher=fake_provider)
    request = read_freshness_json(paths, "data_freshness_refresh_request.json")
    assert request["target_version"] == "v0.9.3-a-share-data-freshness-refresh"
    assert request["requested_target_as_of_date"] == TARGET_DATE
    assert request["resolved_actual_data_date"] == TARGET_DATE
    assert request["dry_run"] is True
    assert request["public_market_data_only"] is True
    assert request["broker_connection_allowed"] is False
    assert "research_pipeline_rerun" in request["excluded_scope"]


def test_data_freshness_actual_refresh_writes_research_market_data(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    assert result["data_refresh_executed"] is True
    assert (paths.data_dir / "equity_universe" / "equity_master.parquet").exists()
    assert (paths.data_dir / "equity_market" / "daily_price_panel.parquet").exists()
    assert (paths.data_dir / "equity_market" / "daily_basic_panel.parquet").exists()
    assert (paths.data_dir / "equity_market" / "adjusted_price_panel.parquet").exists()


def test_data_freshness_dry_run_does_not_write_refreshed_market_data(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, dry_run=True, provider_fetcher=fake_provider)
    assert result["overall_passed"] is True
    assert result["data_refresh_executed"] is False
    assert not (paths.data_dir / "equity_market").exists()


def test_data_freshness_failed_provider_records_blocking_reason(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=failed_provider)
    assert result["overall_passed"] is False
    assert "public_provider_refresh_failed" in result["blocking_reasons"]
    refresh_result = read_freshness_json(paths, "data_freshness_refresh_result.json")
    assert refresh_result["data_refresh_executed"] is False
    assert refresh_result["overall_passed"] is False


def test_data_freshness_partial_coverage_records_blocking_reason(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=partial_provider)
    assert result["overall_passed"] is False
    coverage = read_freshness_json(paths, "data_freshness_coverage_summary.json")
    assert coverage["partial_data_detected"] is True
    assert coverage["coverage_passed"] is False
    assert "coverage_below_minimum_required_ratio" in coverage["coverage_blocking_reasons"]


def test_data_freshness_date_resolution_uses_previous_trading_day(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    resolved = resolve_actual_data_date(paths=paths, target_as_of_date="2026-07-04")
    assert resolved["resolved_actual_data_date"] == "2026-07-03"
    assert resolved["date_resolution_reason"] == "resolved_to_nearest_prior_weekday_fallback"


def test_data_freshness_markdown_report_contains_required_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    report = (paths.outputs_dir / "equity_data_freshness" / "daily" / TARGET_DATE / "A_SHARE_DATA_FRESHNESS_REFRESH_RESULT.md").read_text(encoding="utf-8")
    assert "This refresh updates public market research data only." in report
    assert "This does not rerun research pipeline." in report
    assert "This does not generate candidates, scores, virtual portfolios, or trade signals." in report
    assert "This does not rerun owner-readiness gate." in report
    assert "This does not change owner-readiness blocked state." in report
    assert "This is not investment advice." in report
    assert "This is not live trading ready." in report


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    (root / "work" / "trading-core" / "data").mkdir(parents=True, exist_ok=True)
    (root / "work" / "trading-core" / "outputs").mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def read_freshness_json(paths: ProjectPaths, filename: str) -> dict:
    return json.loads((paths.data_dir / "equity_data_freshness" / "daily" / TARGET_DATE / filename).read_text(encoding="utf-8"))


def fake_provider() -> dict:
    return {"provider": "qstock_reference_public_http", "succeeded": True, "rows": fake_rows(), "external_api_called": True, "reason": "", "raw_total": 3, "raw_coverage_ratio": 1.0}


def failed_provider() -> dict:
    return {"provider": "qstock_reference_public_http", "succeeded": False, "rows": [], "external_api_called": True, "reason": "network unavailable", "raw_total": 0}


def partial_provider() -> dict:
    return {"provider": "qstock_reference_public_http", "succeeded": True, "rows": fake_rows()[:1], "external_api_called": True, "reason": "partial response", "raw_total": 3, "raw_coverage_ratio": 0.333333}


def fake_rows() -> list[dict]:
    return [
        {"f12": "600001", "f14": "Alpha", "f2": 10.0, "f3": 1.0, "f4": 0.1, "f5": 1000, "f6": 10000.0, "f8": 1.2, "f9": 12.0, "f15": 10.5, "f16": 9.8, "f17": 10.1, "f18": 9.9, "f20": 1000000.0, "f21": 800000.0, "f23": 1.5, "f26": "20200101"},
        {"f12": "000001", "f14": "Beta", "f2": 20.0, "f3": 2.0, "f4": 0.2, "f5": 2000, "f6": 40000.0, "f8": 2.2, "f9": 13.0, "f15": 20.5, "f16": 19.8, "f17": 20.1, "f18": 19.9, "f20": 2000000.0, "f21": 1800000.0, "f23": 2.5, "f26": "20200102"},
        {"f12": "830001", "f14": "Gamma", "f2": 30.0, "f3": 3.0, "f4": 0.3, "f5": 3000, "f6": 90000.0, "f8": 3.2, "f9": 14.0, "f15": 30.5, "f16": 29.8, "f17": 30.1, "f18": 29.9, "f20": 3000000.0, "f21": 2800000.0, "f23": 3.5, "f26": "20200103"},
    ]
