from __future__ import annotations

from pathlib import Path

from test_a_share_data_freshness_refresh import TARGET_DATE, fake_provider, make_paths, read_freshness_json
from trading_core.equity_data_freshness import refresh_a_share_data_freshness


def test_data_freshness_boundary_forbids_trading_and_pipeline_actions(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    boundary = read_freshness_json(paths, "data_freshness_boundary_check.json")
    assert boundary["public_market_data_refresh_only"] is True
    assert boundary["data_refresh_executed"] is True
    assert boundary["public_network_refresh_run"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_account_data_read"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["research_pipeline_rerun"] is False
    assert boundary["build_from_existing_data_run"] is False
    assert boundary["owner_daily_pack_run"] is False
    assert boundary["owner_readiness_gate_rerun"] is False
    assert boundary["new_gate_score_generated"] is False
    assert boundary["new_gate_decision_generated"] is False
    assert boundary["threshold_lowered"] is False
    assert boundary["auto_waiver_allowed"] is False
    assert boundary["manual_waiver_approval_recorded"] is False
    assert boundary["old_run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["live_trading_ready"] is False
    assert boundary["data_freshness_used_as_trade_instruction"] is False


def test_data_freshness_manifest_links_core_artifacts(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    manifest = read_freshness_json(paths, "data_freshness_manifest.json")
    assert manifest["source_version"] == "v0.9.2-a-share-owner-daily-runbook-cli-entry-and-staleness-awareness"
    assert manifest["refresh_result_path"].endswith("data_freshness_refresh_result.json")
    assert manifest["provider_status_path"].endswith("data_freshness_provider_status.json")
    assert manifest["coverage_summary_path"].endswith("data_freshness_coverage_summary.json")
    assert manifest["boundary_check_path"].endswith("data_freshness_boundary_check.json")
    assert manifest["markdown_report_path"].endswith("A_SHARE_DATA_FRESHNESS_REFRESH_RESULT.md")
    assert manifest["overall_passed"] is True
