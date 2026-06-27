from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_score_test_utils import build_score_package, make_score_paths, score_data_dir
from trading_core.equity_scoring.scoring_audit import FORBIDDEN_POSITIVE_WORDING, audit_a_share_scores


def test_scoring_boundaries_block_candidates_watchlists_portfolios_signals_and_live_claims(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)
    output_dir = paths.outputs_dir / "equity_scores" / "daily" / AS_OF_DATE
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "WATCHLIST.md").write_text("watchlist placeholder", encoding="utf-8")
    (paths.data_dir / "equity_portfolios").mkdir(parents=True, exist_ok=True)

    summary_path = score_data_dir(paths) / "scoring_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["boundary"]["live_trading_ready"] = True
    summary_path.write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")

    audit = audit_a_share_scores(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is False
    assert audit["forbidden_artifacts"]["watchlist_artifacts_present"]
    assert audit["forbidden_artifacts"]["virtual_portfolio_artifacts_present"]
    assert audit["forbidden_wording_hits"]
    assert "no_profit_or_live_trading_wording=false" in audit["blocking_reasons"]
    assert any("live_trading_ready" in reason for reason in audit["blocking_reasons"])
    assert '"live_trading_ready": true' in FORBIDDEN_POSITIVE_WORDING
