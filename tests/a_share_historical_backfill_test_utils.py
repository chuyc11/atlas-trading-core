from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from tests.a_share_final_closeout_test_utils import seed_v095_and_build_v096
from tests.a_share_research_evidence_test_utils import AS_OF_DATE
from trading_core.equity_readiness_final_closeout import audit_a_share_final_not_ready_closeout


LOOKBACK_START = "2026-06-19"


def seed_v096_with_historical_inputs(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    audit_a_share_final_not_ready_closeout(paths=paths, as_of_date=AS_OF_DATE)
    _seed_calendar(paths)
    _seed_history_panels(paths)
    return paths


def seed_research_outputs(paths, date: str) -> None:
    _write_json(paths.data_dir / "equity_features" / "daily" / date / "feature_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_scores" / "daily" / date / "score_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_selection" / "daily" / date / "candidate_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_manifest.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_source_trace.json", {"as_of_date": date})
    _write_json(paths.data_dir / "equity_briefings" / "daily" / date / "briefing_boundary_check.json", {"overall_passed": True})


def build_v097(paths, monkeypatch, *, successful_days=()):
    from trading_core.equity_historical_evidence_backfill import builder

    successful = set(successful_days)

    def fake_backfill(paths, day):
        if day in successful:
            seed_research_outputs(paths, day)
            return {"date": day, "passed": True, "blocking_reasons": [], "warnings": [], "output_paths": []}
        return {"date": day, "passed": False, "blocking_reasons": ["strict_tradable_universe_empty"], "warnings": [], "output_paths": []}

    monkeypatch.setattr(builder, "_run_historical_research_day", fake_backfill)
    return builder.build_a_share_historical_evidence_backfill_and_refresh_plan(
        paths=paths,
        as_of_date=AS_OF_DATE,
        lookback_start=LOOKBACK_START,
        target_evidence_days=5,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def historical_json(paths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_historical_research_backfill" / "daily" / AS_OF_DATE / f"{name}.json")


def recomputed_json(paths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_research_evidence_recomputed" / "daily" / AS_OF_DATE / f"{name}.json")


def closeout_json(paths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_reevaluation_readiness_closeout" / "daily" / AS_OF_DATE / f"{name}.json")


def refresh_json(paths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_post_close_refresh_planning" / "daily" / AS_OF_DATE / f"{name}.json")


def _seed_calendar(paths) -> None:
    rows = []
    trading_days = {"2026-06-19", "2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26", "2026-06-29", "2026-06-30", "2026-07-01"}
    for day in pd.date_range("2026-06-19", "2026-07-01", freq="D").strftime("%Y-%m-%d"):
        rows.append({"date": day, "exchange": "SSE", "is_trading_day": day in trading_days})
    path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def _seed_history_panels(paths) -> None:
    days = ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25"]
    rows = [{"date": day, "symbol": "000001.SZ", "close": 10.0, "volume": 1000, "amount": 10000, "total_mv": 1, "circ_mv": 1} for day in days]
    base = pd.DataFrame(rows)
    market = paths.data_dir / "equity_market" / "history"
    market.mkdir(parents=True, exist_ok=True)
    base[["date", "symbol", "close", "volume", "amount"]].to_parquet(market / "daily_price_history_panel.parquet", index=False)
    base[["date", "symbol", "close"]].rename(columns={"close": "adj_close"}).to_parquet(market / "adjusted_price_history_panel.parquet", index=False)
    base[["date", "symbol", "total_mv", "circ_mv"]].to_parquet(market / "daily_basic_history_panel.parquet", index=False)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
