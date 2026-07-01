from __future__ import annotations

import json
from pathlib import Path

from trading_core.storage.file_paths import ProjectPaths

AS_OF_DATE = "2026-07-01"
BASELINE_DATE = "2026-06-26"


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    (project / "data").mkdir(parents=True, exist_ok=True)
    (project / "outputs").mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def seed_research_evidence_inputs(paths: ProjectPaths, *, include_second_day: bool = True) -> None:
    _seed_day(paths, AS_OF_DATE)
    if include_second_day:
        _seed_day(paths, BASELINE_DATE)
    _write_json(
        paths.data_dir / "equity_data_freshness" / "daily" / AS_OF_DATE / "data_freshness_refresh_result.json",
        {
            "overall_passed": True,
            "resolved_actual_data_date": AS_OF_DATE,
            "warnings": ["missing_quote_symbol_count=355"],
        },
    )
    _write_json(
        paths.data_dir / "equity_data_freshness" / "daily" / AS_OF_DATE / "data_freshness_coverage_summary.json",
        {"coverage_passed": True, "coverage_ratio": 1.0, "missing_symbol_count": 0, "missing_quote_symbol_count": 355},
    )
    _write_json(
        paths.data_dir / "equity_research_pipeline_rerun" / "daily" / AS_OF_DATE / "research_pipeline_rerun_result.json",
        {
            "overall_passed": True,
            "as_of_date": AS_OF_DATE,
            "source_data_date": AS_OF_DATE,
            "build_from_existing_data_run": True,
            "research_pipeline_rerun": True,
            "owner_readiness_gate_rerun": False,
            "controlled_gate_reevaluation_run": False,
            "new_gate_score_generated": False,
            "new_gate_decision_generated": False,
        },
    )
    _write_json(
        paths.data_dir / "equity_research_pipeline_rerun" / "daily" / AS_OF_DATE / "research_pipeline_boundary_check.json",
        {
            "overall_passed": True,
            "broker_connected": False,
            "real_account_data_read": False,
            "real_orders_placed": False,
            "order_preview_generated": False,
            "buy_sell_signals_generated": False,
        },
    )
    _write_json(
        paths.data_dir / "equity_owner_closeout_review" / "daily" / BASELINE_DATE / "unresolved_blocker_register.json",
        {
            "unresolved_blocker_count": 6,
            "blockers": [
                _blocker("B001", "readiness_score_gap"),
                _blocker("B002", "missing_recovery_evidence"),
                _blocker("B003", "missing_audit_verified_evidence"),
                _blocker("B004", "remaining_evidence_gaps"),
                _blocker("B005", "owner_readiness_not_acceptable"),
                _blocker("B006", "insufficient_history_if_present"),
            ],
        },
    )
    _write_json(paths.data_dir / "equity_owner_v090_rc" / "daily" / BASELINE_DATE / "v090_audit_sweep_result.json", {"overall_passed": True})
    _write_json(paths.data_dir / "equity_owner_v090_rc" / "daily" / BASELINE_DATE / "v090_full_pytest_result.json", {"passed": 1701, "skipped": 1})


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_a(paths: ProjectPaths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_research_evidence_accumulation" / "daily" / AS_OF_DATE / f"{name}.json")


def phase_b(paths: ProjectPaths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / AS_OF_DATE / f"{name}.json")


def _seed_day(paths: ProjectPaths, date: str) -> None:
    _write_json(paths.data_dir / "equity_features" / "daily" / date / "feature_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_features" / "daily" / date / "feature_generation_summary.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_scores" / "daily" / date / "score_manifest.json", {"as_of_date": date})
    _write_json(
        paths.data_dir / "equity_scores" / "daily" / date / "score_distribution.json",
        {
            "as_of_date": date,
            "scores": {
                "LongScore": {"count": 3, "mean": 51.0},
                "MidScore": {"count": 3, "mean": 50.0},
                "ShortScore": {"count": 3, "mean": 49.0},
            },
        },
    )
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "candidate_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "candidate_generation_summary.json", {"as_of_date": date, "strict_tradable_count": 3, "scored_symbols": 3})
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "long_candidates.json", [{"symbol": "000001.SZ"}, {"symbol": "000002.SZ"}])
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "mid_candidates.json", [{"symbol": "000003.SZ"}])
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "short_candidates.json", [{"symbol": "600001.SH"}])
    _write_json(paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_weight_summary.json", {"long_virtual_portfolio": {"holdings": 2, "weight_sum": 1.0}})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_source_trace.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_boundary_check.json", {"overall_passed": True})
    _write_text(paths.outputs_dir / "equity_briefings" / "daily" / date / "DAILY_STOCK_SELECTION_BRIEFING.md", "Research-only briefing. Not investment advice.")


def _blocker(blocker_id: str, category: str) -> dict:
    return {
        "blocker_id": blocker_id,
        "category": category,
        "source_version": "v0.8.21",
        "description": f"{category} remains open.",
        "blocks_owner_readiness_acceptance": True,
    }


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
