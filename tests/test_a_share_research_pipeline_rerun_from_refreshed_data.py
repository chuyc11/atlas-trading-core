from __future__ import annotations

import json
from pathlib import Path

from trading_core.cli import build_parser, main
from trading_core.equity_research_pipeline_rerun import (
    DEFAULT_AS_OF_DATE,
    TARGET_VERSION,
    rerun_a_share_research_pipeline_from_refreshed_data,
    validate_source_data_freshness,
)
from trading_core.storage.file_paths import ProjectPaths


def test_source_data_freshness_validation_preserves_v093_warning(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    _seed_v093_freshness(paths)

    result = validate_source_data_freshness(paths=paths, as_of_date=DEFAULT_AS_OF_DATE)

    assert result["source_data_validation_passed"] is True
    assert result["resolved_source_data_date"] == DEFAULT_AS_OF_DATE
    assert result["v093_coverage_ratio"] == 1.0
    assert result["v093_missing_symbol_count"] == 0
    assert result["v093_warnings"] == ["missing_quote_symbol_count=355"]
    assert result["missing_quote_warning_assessment"] == "non_blocking_warning_for_pipeline_completeness"


def test_source_data_freshness_validation_fails_closed_on_stale_source(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    _seed_v093_freshness(paths, resolved_actual_data_date="2026-06-26")

    result = validate_source_data_freshness(paths=paths, as_of_date=DEFAULT_AS_OF_DATE)

    assert result["source_data_validation_passed"] is False
    assert "v093_source_data_date_mismatch" in result["blocking_reasons"]


def test_dry_run_writes_control_artifacts_without_research_outputs(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    _seed_v093_freshness(paths)

    result = rerun_a_share_research_pipeline_from_refreshed_data(paths=paths, as_of_date=DEFAULT_AS_OF_DATE, dry_run=True)

    assert result["overall_passed"] is True
    assert result["dry_run"] is True
    assert result["pipeline_execution_passed"] is True
    assert result["research_output_validation_passed"] is True
    assert result["candidate_output_generated"] is False
    assert result["score_output_generated"] is False
    assert not (paths.data_dir / "equity_features" / "daily" / DEFAULT_AS_OF_DATE / "feature_manifest.json").exists()
    assert _json(paths, "research_pipeline_rerun_result")["build_from_existing_data_run"] is False
    assert _json(paths, "research_pipeline_boundary_check")["broker_connected"] is False


def test_actual_rerun_with_research_steps_generates_safe_control_pack(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    _seed_v093_freshness(paths)
    protected = paths.data_dir / "orders" / "existing_order_boundary.txt"
    protected.parent.mkdir(parents=True, exist_ok=True)
    protected.write_text("do-not-touch", encoding="utf-8")

    result = rerun_a_share_research_pipeline_from_refreshed_data(
        paths=paths,
        as_of_date=DEFAULT_AS_OF_DATE,
        step_overrides=_fake_step_overrides(paths),
    )

    assert result["overall_passed"] is True
    assert result["source_data_date"] == DEFAULT_AS_OF_DATE
    assert result["candidate_output_generated"] is True
    assert result["score_output_generated"] is True
    assert result["virtual_portfolio_output_generated"] is True
    assert result["research_briefing_generated"] is True
    assert result["protected_order_trade_account_paths_untouched"] is True
    assert protected.read_text(encoding="utf-8") == "do-not-touch"

    control = _json(paths, "research_pipeline_rerun_result")
    assert control["target_version"] == TARGET_VERSION
    assert control["known_owner_readiness_state"] == "blocked"
    assert control["owner_operationally_acceptable"] is False
    assert control["readiness_score"] == 54
    assert control["minimum_owner_readiness_score"] == 75
    assert control["score_gap"] == 21
    assert control["owner_daily_pack_run"] is False
    assert control["owner_readiness_gate_rerun"] is False
    assert control["controlled_gate_reevaluation_run"] is False
    assert control["new_gate_score_generated"] is False
    assert control["new_gate_decision_generated"] is False
    assert control["broker_connected"] is False
    assert control["real_account_data_read"] is False
    assert control["real_orders_placed"] is False
    assert control["order_preview_generated"] is False
    assert control["buy_sell_signals_generated"] is False
    assert control["old_run_daily_called"] is False
    assert control["day2_executed"] is False

    manifest = _json(paths, "research_pipeline_manifest")
    assert manifest["overall_passed"] is True
    assert (paths.outputs_dir / "equity_research_pipeline_rerun" / "daily" / DEFAULT_AS_OF_DATE / "A_SHARE_RESEARCH_PIPELINE_RERUN_RESULT.md").exists()


def test_research_pipeline_rerun_cli_registered() -> None:
    args = build_parser().parse_args(["rerun-a-share-research-pipeline-from-refreshed-data", "--as-of-date", DEFAULT_AS_OF_DATE, "--dry-run"])
    assert args.command == "rerun-a-share-research-pipeline-from-refreshed-data"
    assert args.as_of_date == DEFAULT_AS_OF_DATE
    assert args.dry_run is True


def test_research_pipeline_rerun_cli_smoke(tmp_path: Path, monkeypatch, capsys) -> None:
    import trading_core.cli as cli

    paths = _make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(
        cli,
        "rerun_a_share_research_pipeline_from_refreshed_data",
        lambda **kwargs: {
            "builder_id": "A-SHARE-RESEARCH-PIPELINE-RERUN",
            "target_version": TARGET_VERSION,
            "as_of_date": kwargs["as_of_date"],
            "source_data_date": kwargs["as_of_date"],
            "dry_run": kwargs["dry_run"],
            "overall_passed": True,
            "source_data_freshness_validation_passed": True,
            "pipeline_execution_passed": True,
            "research_output_validation_passed": True,
            "candidate_output_generated": False,
            "score_output_generated": False,
            "virtual_portfolio_output_generated": False,
            "research_briefing_generated": False,
            "protected_order_trade_account_paths_untouched": True,
            "blocking_reasons": [],
            "warnings": ["missing_quote_symbol_count=355"],
            "recommended_next_version": "v0.9.5-a-share-multi-day-research-output-evidence-accumulation",
        },
    )

    assert main(["rerun-a-share-research-pipeline-from-refreshed-data", "--as-of-date", DEFAULT_AS_OF_DATE, "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-RESEARCH-PIPELINE-RERUN" in out
    assert "missing_quote_symbol_count=355" in out


def _make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    (project / "data").mkdir(parents=True, exist_ok=True)
    (project / "outputs").mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def _seed_v093_freshness(paths: ProjectPaths, *, resolved_actual_data_date: str = DEFAULT_AS_OF_DATE) -> None:
    root = paths.data_dir / "equity_data_freshness" / "daily" / DEFAULT_AS_OF_DATE
    _write_json(
        root / "data_freshness_refresh_result.json",
        {
            "overall_passed": True,
            "resolved_actual_data_date": resolved_actual_data_date,
            "data_refresh_executed": True,
            "public_network_refresh_run": True,
            "blocking_reasons": [],
            "warnings": ["missing_quote_symbol_count=355"],
        },
    )
    _write_json(root / "data_freshness_coverage_summary.json", {"coverage_passed": True, "coverage_ratio": 1.0, "missing_symbol_count": 0, "missing_quote_symbol_count": 355})
    _write_json(root / "data_freshness_provider_status.json", {"overall_provider_status": "passed"})


def _fake_step_overrides(paths: ProjectPaths) -> dict:
    def tradable_universe_refresh(**kwargs):
        as_of_date = kwargs["config"].as_of_date
        path = paths.data_dir / "equity_selection" / "daily" / as_of_date / "tradable_universe_manifest.json"
        _write_json(path, {"as_of_date": as_of_date})
        return {"manifest_path": str(path), "blocking_reasons": [], "warnings": []}

    def feature_refresh(**kwargs):
        return _write_manifest(paths.data_dir / "equity_features" / "daily" / kwargs["as_of_date"] / "feature_manifest.json")

    def research_score_refresh(**kwargs):
        return _write_manifest(paths.data_dir / "equity_scores" / "daily" / kwargs["as_of_date"] / "score_manifest.json")

    def research_candidate_refresh(**kwargs):
        return _write_manifest(paths.data_dir / "equity_selection" / "daily" / kwargs["as_of_date"] / "candidate_manifest.json")

    def virtual_only_portfolio_research_refresh(**kwargs):
        return _write_manifest(paths.data_dir / "equity_portfolios" / "daily" / kwargs["as_of_date"] / "portfolio_manifest.json")

    def research_briefing_refresh(**kwargs):
        return _write_manifest(paths.data_dir / "equity_briefings" / "daily" / kwargs["as_of_date"] / "briefing_manifest.json")

    return {
        "tradable_universe_refresh": tradable_universe_refresh,
        "feature_refresh": feature_refresh,
        "research_score_refresh": research_score_refresh,
        "research_candidate_refresh": research_candidate_refresh,
        "virtual_only_portfolio_research_refresh": virtual_only_portfolio_research_refresh,
        "research_briefing_refresh": research_briefing_refresh,
    }


def _write_manifest(path: Path) -> dict:
    _write_json(path, {"path": str(path), "blocking_reasons": [], "warnings": []})
    return {"manifest_path": str(path), "blocking_reasons": [], "warnings": []}


def _json(paths: ProjectPaths, key: str) -> dict:
    path = paths.data_dir / "equity_research_pipeline_rerun" / "daily" / DEFAULT_AS_OF_DATE / f"{key}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
